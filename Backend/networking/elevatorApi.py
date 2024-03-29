import dataclasses
import logging
import os
from typing import Optional
from urllib.parse import urljoin

import aiohttp
import aiohttp_client_cache
from aiohttp import ClientConnectorError
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.networking.http import NetworkBase
from Backend.networking.schemas import WebResponse

elevator_route = f"""http://{os.environ.get("ELEVATOR_HOST")}:{os.environ.get("ELEVATOR_PORT")}/"""


@dataclasses.dataclass
class ElevatorApi(NetworkBase):
    db: Optional[AsyncSession] = None

    def __post_init__(self):
        self.request_retries = 1

    async def post(
        self, route: str, json: Optional[dict] = None, params: Optional[dict] = None
    ) -> Optional[WebResponse]:
        """Post Request. Return None if Elevator is offline"""

        return await self._request(
            method="POST",
            route=urljoin(elevator_route, route),
            json=json,
            params=params,
        )

    async def get(self, route: str, params: dict | None = None, *kwargs) -> Optional[WebResponse]:
        """Get Request. Return None if Elevator is offline"""

        return await self._request(
            method="GET",
            route=urljoin(elevator_route, route),
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

        try:
            return await super()._request(
                method=method,
                route=route.removesuffix("/"),
                params=params,
                json=json,
            )
        except ClientConnectorError:
            # if it can't connect to elevator
            return None
