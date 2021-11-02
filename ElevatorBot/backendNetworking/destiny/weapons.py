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


@dataclasses.dataclass
class DestinyWeapons(BaseBackendConnection):
    client: Optional[Snake]
    discord_guild: Optional[Guild]
    discord_member: Optional[Member]

    async def get_all(self) -> BackendResult:
        """Get all weapons"""

        return await self._backend_request(
            method="GET",
            route=destiny_weapons_get_all_route,
        )

    async def get_top(self) -> BackendResult:
        """Get top weapons"""

        return await self._backend_request(
            method="GET",
            route=destiny_weapons_get_top_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
            data={},  # todo
        )

    async def get_weapon(self) -> BackendResult:
        """Get the specified weapon stat"""

        return await self._backend_request(
            method="GET",
            route=destiny_weapons_get_weapon_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
            data={},  # todo
        )
