import dataclasses
from typing import Optional

from dis_snek.client import Snake
from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import (
    destiny_weapons_get_all_route,
    destiny_weapons_get_top_route,
    destiny_weapons_get_weapon_route,
)
from NetworkingSchemas.destiny.weapons import DestinyWeaponsModel


@dataclasses.dataclass
class DestinyWeapons(BaseBackendConnection):
    client: Optional[Snake]
    discord_guild: Optional[Guild]
    discord_member: Optional[Member]

    async def get_all(self) -> Optional[DestinyWeaponsModel]:
        """Get all weapons"""

        result = await self._backend_request(
            method="GET",
            route=destiny_weapons_get_all_route,
        )

        # convert to correct pydantic model
        return DestinyWeaponsModel.parse_obj(result.result) if result else None

    async def get_top(self) -> Optional[aaaaaaaaaaaaaa]:
        """Get top weapons"""

        result = await self._backend_request(
            method="GET",
            route=destiny_weapons_get_top_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
            data={},  # todo
        )

        # convert to correct pydantic model
        return aaaaaaaaaaaaaa.parse_obj(result.result) if result else None

    async def get_weapon(self) -> Optional[aaaaaaaaaaaaaa]:
        """Get the specified weapon stat"""

        result = await self._backend_request(
            method="GET",
            route=destiny_weapons_get_weapon_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
            data={},  # todo
        )

        # convert to correct pydantic model
        return aaaaaaaaaaaaaa.parse_obj(result.result) if result else None
