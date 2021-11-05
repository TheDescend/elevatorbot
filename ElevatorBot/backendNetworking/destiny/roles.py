import dataclasses
from typing import Optional

from dis_snek.client import Snake
from dis_snek.models.discord_objects.guild import Guild
from dis_snek.models.discord_objects.role import Role

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    destiny_role_get_all_user_route,
    destiny_role_get_missing_user_route,
    destiny_role_get_user_route,
)
from NetworkingSchemas.destiny.roles import (
    EarnedRoleModel,
    EarnedRolesModel,
    MissingRolesModel,
)


@dataclasses.dataclass
class DestinyRoles(BaseBackendConnection):
    client: Snake
    discord_guild: Guild

    async def get(self) -> Optional[EarnedRolesModel]:
        """Get the users roles in the guild"""

        result = await self._backend_request(
            method="GET",
            route=destiny_role_get_all_user_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return EarnedRolesModel.parse_obj(result.result) if result else None

    async def get_missing(self) -> Optional[MissingRolesModel]:
        """Get the users missing roles in the guild"""

        result = await self._backend_request(
            method="GET",
            route=destiny_role_get_missing_user_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return MissingRolesModel.parse_obj(result.result) if result else None

    async def get_detail(self, role: Role) -> Optional[EarnedRoleModel]:
        """Get the details for the users role completion"""

        result = await self._backend_request(
            method="GET",
            route=destiny_role_get_user_route.format(
                guild_id=self.discord_guild.id, role_id=role.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return EarnedRoleModel.parse_obj(result.result) if result else None
