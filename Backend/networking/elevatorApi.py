import dataclasses
import logging
import os
from typing import Optional

import aiohttp
from aiohttp import ClientConnectorError
from orjson import orjson

from Backend.networking.base import NetworkBase
from Backend.networking.schemas import WebResponse


class ElevatorOffline(Exception):
    pass


@dataclasses.dataclass
class ElevatorApi(NetworkBase):
    logger = logging.getLogger("elevatorApi")

    route = f"""http://{os.environ.get("ELEVATOR_HOST")}:{os.environ.get("ELEVATOR_PORT")}/"""

    bungie_request: bool = False

    async def post(
        self, route_addition: str, json: Optional[dict] = None, params: Optional[dict] = None
    ) -> Optional[WebResponse]:
        """Post Request. Return None if Elevator is offline"""

        return await self._elevator_request(
            method="POST",
            route=self.route + route_addition,
            json=json,
            params=params,
        )

    async def get(self, route_addition: str, params: Optional[dict] = None) -> Optional[WebResponse]:
        """Get Request. Return None if Elevator is offline"""

        return await self._elevator_request(
            method="GET",
            route=self.route + route_addition,
            params=params,
        )

    async def _elevator_request(
        self, method: str, route: str, params: Optional[dict] = None, json: Optional[dict] = None
    ) -> Optional[WebResponse]:
        """Reduce duplication"""

        async with aiohttp.ClientSession(json_serialize=lambda x: orjson.dumps(x).decode()) as session:
            try:
                return await self._request(
                    session=session,
                    method=method,
                    route=route,
                    params=params,
                    json=json,
                )
            except ClientConnectorError:
                # if it can't connect to elevator
                return None
