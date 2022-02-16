import logging
import os
from typing import Optional
from urllib.parse import urlencode, urljoin

import aiohttp
import aiohttp_client_cache
from aiohttp import ClientConnectorError
from orjson import orjson

from Backend.core.errors import CustomException
from Backend.networking.base import NetworkBase
from Backend.networking.schemas import InternalWebResponse, WebResponse


class ElevatorOffline(Exception):
    pass


class ElevatorApi(NetworkBase):
    logger = logging.getLogger("elevatorApi")
    logger_exceptions = logging.getLogger("elevatorApiExceptions")

    route = f"""http://{os.environ.get("ELEVATOR_HOST")}:{os.environ.get("ELEVATOR_PORT")}/"""

    bungie_request: bool = False
    max_web_request_tries: int = 1

    async def post(
        self, route_addition: str, json: Optional[dict] = None, params: Optional[dict] = None
    ) -> Optional[WebResponse]:
        """Post Request. Return None if Elevator is offline"""

        return await self._elevator_request(
            method="POST",
            route=urljoin(self.route, route_addition),
            json=json,
            params=params,
        )

    async def get(self, route_addition: str, params: Optional[dict] = None) -> Optional[WebResponse]:
        """Get Request. Return None if Elevator is offline"""

        return await self._elevator_request(
            method="GET",
            route=urljoin(self.route, route_addition),
            params=params,
        )

    async def _elevator_request(
        self, method: str, route: str, params: Optional[dict] = None, json: Optional[dict] = None
    ) -> Optional[WebResponse]:
        """Reduce duplication"""

        self.request_handler = self.__handle_elevator_request_data

        async with aiohttp.ClientSession(json_serialize=lambda x: orjson.dumps(x).decode()) as session:
            try:
                return await self._request(
                    session=session,
                    method=method,
                    route=route.removesuffix("/"),
                    params=params,
                    json=json,
                )
            except ClientConnectorError:
                # if it can't connect to elevator
                return None

    async def __handle_elevator_request_data(
        self,
        request: aiohttp.ClientResponse | aiohttp_client_cache.CachedResponse,
        route: str,
        params: Optional[dict],
    ) -> Optional[InternalWebResponse]:
        """Overwrite the bungie handler"""

        if not params:
            params = {}
        route_with_params = f"{route}?{urlencode(params)}"

        try:
            response = await request.json(loads=orjson.loads)
        except aiohttp.ContentTypeError:
            response = await request.text()

        match request.status:
            case 404:
                # not found
                self.logger_exceptions.error(f"'{response.status}': Not Found for '{route_with_params}' - '{response}'")

            case 200:
                return InternalWebResponse(
                    content=response,
                    status=request.status,
                )

            # wildcard error
            case _:
                self.logger_exceptions.error(
                    f"'{request.status}': Request failed for '{route_with_params}' - '{response}'"
                )

        raise CustomException("ProgrammingError")
