import dataclasses
import logging
import os
from typing import Optional
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientConnectorError
from orjson import orjson

from Backend.core.errors import CustomException
from Backend.networking.http import NetworkBase
from Backend.networking.schemas import WebResponse

elevator_route = f"""http://{os.environ.get("ELEVATOR_HOST")}:{os.environ.get("ELEVATOR_PORT")}/"""


@dataclasses.dataclass
class ElevatorApi(NetworkBase):
    def __post_init__(self):
        self.request_retries = 1
        self.logger = logging.getLogger("elevatorApi")
        self.logger_exceptions = logging.getLogger("elevatorApiExceptions")

    async def post(
        self, route_addition: str, json: Optional[dict] = None, params: Optional[dict] = None
    ) -> Optional[WebResponse]:
        """Post Request. Return None if Elevator is offline"""

        return await self._request(
            method="POST",
            route=urljoin(elevator_route, route_addition),
            json=json,
            params=params,
        )

    async def get(self, route_addition: str, params: Optional[dict] = None) -> Optional[WebResponse]:
        """Get Request. Return None if Elevator is offline"""

        return await self._request(
            method="GET",
            route=urljoin(elevator_route, route_addition),
            params=params,
        )

    async def _request(
        self,
        method: str,
        route: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        *args,
        **kwargs,
    ) -> Optional[WebResponse]:
        """Reduce duplication"""

        async with aiohttp.ClientSession(json_serialize=lambda x: orjson.dumps(x).decode()) as session:
            try:
                return await super()._request(
                    session=session,
                    method=method,
                    route=route.removesuffix("/"),
                    params=params,
                    json=json,
                )
            except ClientConnectorError:
                # if it can't connect to elevator
                return None

    async def _handle_errors(self, response: WebResponse, route_with_params: str):
        """Handle the elevator request results"""

        match response.status:
            case 404:
                # not found
                self.logger_exceptions.error(f"'{response.status}': Not Found for '{route_with_params}' - '{response}'")

            # wildcard error
            case _:
                self.logger_exceptions.error(
                    f"'{response.status}': Request failed for '{route_with_params}' - '{response}'"
                )

        raise CustomException("ProgrammingError")
