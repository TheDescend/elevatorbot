import asyncio
import dataclasses
import logging
import random
from typing import Optional
from urllib.parse import urlencode

import aiohttp
import aiohttp_client_cache
from aiohttp import ServerDisconnectedError
from orjson import orjson
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.networking.schemas import WebResponse
from Shared.functions.helperFunctions import get_now_with_tz


@dataclasses.dataclass
class NetworkBase:
    db: AsyncSession

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

        async with aiohttp.ClientSession(json_serialize=lambda x: orjson.dumps(x).decode()) as session:
            return await self._request(
                session=session,
                method="GET",
                route=route,
                headers=headers,
                params=params,
            )

    async def _request(
        self,
        session: aiohttp_client_cache.CachedSession | aiohttp.ClientSession,
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
        for _ in range(self.request_retries):
            try:
                async with session.request(
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

            except (asyncio.exceptions.TimeoutError, ConnectionResetError, ServerDisconnectedError) as error:
                self.logger.warning(
                    f"Retrying... - Timeout error ('{error}') for '{route}?{urlencode({} if params is None else params)}'"
                )
                await asyncio.sleep(random.randrange(2, 6))
                continue

        # return that it failed
        self.logger_exceptions.error(f"Request failed '{self.request_retries}' times, aborting for '{route}'")
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
        content_type = (
            request.headers.get("Content-Type", "NOT SET")
            if not hasattr(request, "content_type")
            else request.content_type
        )

        # catch the content type "application/octet-stream" which is returned for some routes
        if "application/octet-stream" in content_type:
            # this is issued with a 301 when bungie is of the opinion that resource this moved (which is wrong, depending on server)
            # just retrying fixes it with the new url fixes it
            if request.status == 301:
                self.route = request.headers.get("Location")
                return

        # make sure the return is a json, sometimes we get a http file for some reason
        elif "application/json" not in content_type:
            self.logger_exceptions.error(
                f"""'{request.status}': Retrying... - Wrong content type '{content_type}' with reason '{request.reason}' for '
                {route_with_params}'"""
            )
            print(f"""Bungie returned Content-Type: {content_type}""")
            if request.status == 200:
                self.logger_exceptions.error(f"Wrong content type returned text: '{await request.text()}'")
            await asyncio.sleep(3)
            return

        #  set if the response was cached
        try:
            from_cache = request.from_cache
        except AttributeError:
            from_cache = False

        # get the response as a json
        try:
            response = WebResponse(
                content=await request.json(loads=orjson.loads),
                status=request.status,
                from_cache=from_cache,
                time=get_now_with_tz(),
            )
        except aiohttp.ClientPayloadError:
            self.logger_exceptions.error(f"'{request.status}': Payload error, retrying for '{route_with_params}'")
            return
        except aiohttp.ContentTypeError:
            return

        # if response is ok return it
        if response.status == 200:
            # remove the leading "Response" from the request (if exists)
            if "Response" in response.content:
                response.content = response.content["Response"]

            return response

        # handling any errors if not ok
        await self._handle_errors(response=response, route_with_params=route_with_params)

    async def _handle_errors(self, response: WebResponse, route_with_params: str):
        raise NotImplementedError
