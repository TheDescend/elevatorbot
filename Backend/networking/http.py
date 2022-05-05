import asyncio
import dataclasses
import logging
import random
from typing import Optional
from urllib.parse import urlencode

import aiohttp
import aiohttp_client_cache
from aiohttp import ClientConnectorCertificateError, ClientConnectorError, ClientSession, ServerDisconnectedError
from aiohttp_client_cache import CachedSession
from orjson import orjson
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.networking.schemas import WebResponse
from Shared.functions.helperFunctions import get_now_with_tz


@dataclasses.dataclass
class RouteError(Exception):
    route: str


@dataclasses.dataclass
class NetworkBase:
    db: AsyncSession

    session: ClientSession | CachedSession = dataclasses.field(
        init=False, default=ClientSession(json_serialize=lambda x: orjson.dumps(x).decode())
    )

    # get logger
    logger: logging.Logger = dataclasses.field(init=False, default=logging.getLogger("bungieApi"))
    logger_exceptions: logging.Logger = dataclasses.field(init=False, default=logging.getLogger("bungieApiExceptions"))

    # how many times to retry a request
    request_retries: int = dataclasses.field(init=False, default=10)

    async def get(
        self,
        route: str,
        headers: dict,
        params: dict | None = None,
    ) -> WebResponse:
        """Grabs JSON from the specified URL"""

        return await self._request(
            method="GET",
            route=route,
            headers=headers,
            params=params,
        )

    async def _request(
        self,
        method: str,
        route: str,
        allow_redirects: bool = True,
        headers: dict = None,
        params: dict = None,
        json: dict = None,
        form_data: dict = None,
    ) -> WebResponse:
        """Make a request to the url with the method and handles the result"""

        assert not (form_data and json), "Only json or form_data can be used"

        # abort after self.request_retries tries
        for i in range(self.request_retries):
            # take a rate limiter token
            if hasattr(self, "limiter"):
                await self.limiter.wait_for_token()

            try:
                async with self.session.request(
                    method=method,
                    url=route,
                    headers=headers,
                    params=params,
                    json=json,
                    data=form_data,
                    allow_redirects=allow_redirects,
                ) as request:
                    # parse the response
                    response = await self._handle_request_data(
                        request=request,
                        params=params,
                        route=route,
                    )

                    # try again
                    if response is None:
                        continue

                    # otherwise, return response
                    return response
            except RouteError as error:
                route = error.route
                continue

            except (
                asyncio.exceptions.TimeoutError,
                ConnectionResetError,
                ServerDisconnectedError,
                ClientConnectorCertificateError,
            ) as error:
                self.logger.warning(
                    f"Retrying... - Timeout error for `{route}?{urlencode({} if params is None else params)}`",
                    exc_info=error,
                )
                await asyncio.sleep(random.randrange(2, 6))
                continue

            except ClientConnectorError:
                raise

            except Exception as error:
                self.logger.exception(
                    f"Unknown error `{type(error)}` for `{route}?{urlencode({} if params is None else params)}`",
                    exc_info=error,
                )
                raise error

        # return that it failed
        self.logger_exceptions.exception(f"Request failed `{self.request_retries}` times, aborting for `{route}`")
        raise CustomException("UnknownError")

    async def _handle_request_data(
        self,
        request: aiohttp.ClientResponse | aiohttp_client_cache.CachedResponse,
        route: str,
        params: Optional[dict],
    ) -> Optional[WebResponse]:
        """Handle the bungie request results"""

        route_with_params = f"{route}?{urlencode(params or {})}"

        # cached responses do not have the content type field
        content_type = getattr(request, "content_type", None) or request.headers.get("Content-Type", "NOT SET")

        # get the json
        content = await request.json(loads=orjson.loads) if "application/json" in content_type else None

        # handle status codes
        if not await self._handle_status_codes(request=request, route_with_params=route_with_params, content=content):
            return

        # clean the json
        if content:
            if "Response" in content:
                content = content["Response"]
        return WebResponse(
            content=content,
            status=request.status,
            from_cache=getattr(request, "from_cache", False),
            time=get_now_with_tz(),
        )

    async def _handle_status_codes(
        self,
        request: aiohttp.ClientResponse | aiohttp_client_cache.CachedResponse,
        route_with_params: str,
        content: Optional[dict] = None,
    ) -> bool:
        """Handle the elevator request results"""

        match request.status:
            case 200:
                return True

            case 404:
                # not found
                self.logger_exceptions.exception(f"`{request.status}`: Not Found for `{route_with_params}`\n{content}")

            # wildcard error
            case _:
                self.logger_exceptions.exception(
                    f"`{request.status}`: Request failed for `{route_with_params}`\n{content}"
                )

        raise CustomException("ProgrammingError")
