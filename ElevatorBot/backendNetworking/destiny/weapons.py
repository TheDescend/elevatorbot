import dataclasses
from typing import Optional

from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    destiny_weapons_get_all_route,
    destiny_weapons_get_top_route,
    destiny_weapons_get_weapon_route,
)
from Shared.networkingSchemas.destiny import (
    DestinyTopWeaponsInputModel,
    DestinyTopWeaponsModel,
    DestinyWeaponsModel,
    DestinyWeaponStatsInputModel,
    DestinyWeaponStatsModel,
)


@dataclasses.dataclass
class DestinyWeapons(BaseBackendConnection):
    discord_guild: Optional[Guild]
    discord_member: Optional[Member]

    async def get_all(self) -> DestinyWeaponsModel:
        """Get all weapons"""

        result = await self._backend_request(
            method="GET",
            route=destiny_weapons_get_all_route,
        )

        # convert to correct pydantic model
        return DestinyWeaponsModel.parse_obj(result.result)

    async def get_top(
        self, input_data: DestinyTopWeaponsInputModel, discord_id: Optional[int] = None
    ) -> DestinyTopWeaponsModel:
        """Get top weapons"""

        assert self.discord_member or discord_id

        result = await self._backend_request(
            method="POST",
            route=destiny_weapons_get_top_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id if self.discord_member else discord_id
            ),
            data=input_data,
        )

        # convert to correct pydantic model
        return DestinyTopWeaponsModel.parse_obj(result.result)

    async def get_weapon(self, input_data: DestinyWeaponStatsInputModel) -> DestinyWeaponStatsModel:
        """Get the specified weapon stat"""

        result = await self._backend_request(
            method="POST",
            route=destiny_weapons_get_weapon_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
            data=input_data,
        )

        # convert to correct pydantic model
        return DestinyWeaponStatsModel.parse_obj(result.result)
