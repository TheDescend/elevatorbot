import dataclasses
from typing import Optional

from dis_snek import Snake

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    destiny_collectible_name_route,
    destiny_triumph_name_route,
)
from NetworkingSchemas.destiny.account import DestinyNameModel


@dataclasses.dataclass
class DestinyItems(BaseBackendConnection):
    async def get_triumph_name(self, triumph_id: int) -> Optional[DestinyNameModel]:
        """Return the triumph name"""

        result = await self._backend_request(
            method="GET",
            route=destiny_triumph_name_route.format(triumph_id=triumph_id),
        )

        # convert to correct pydantic model
        return DestinyNameModel.parse_obj(result.result) if result else None

    async def get_collectible_name(self, collectible_id: int) -> Optional[DestinyNameModel]:
        """Return the collectible name"""

        result = await self._backend_request(
            method="GET",
            route=destiny_collectible_name_route.format(collectible_id=collectible_id),
        )

        # convert to correct pydantic model
        return DestinyNameModel.parse_obj(result.result) if result else None
