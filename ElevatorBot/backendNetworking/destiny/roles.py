import dataclasses

from dis_snek.client import Snake
from dis_snek.models.discord_objects.guild import Guild
from dis_snek.models.discord_objects.role import Role

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import (
    destiny_role_get_all_user_route,
    destiny_role_get_missing_user_route,
    destiny_role_get_user_route,
)
from NetworkingSchemas.destiny.roles import (
    EarnedRoleModel,
    EarnedRolesModel,
    MissingRolesModel,
    RolesModel,
)


@dataclasses.dataclass
class DestinyRoles(BaseBackendConnection):
    client: Snake
    discord_guild: Guild

    async def get(self) -> BackendResult:
        """Get the users roles in the guild"""

        result = await self._backend_request(
            method="GET",
            route=destiny_role_get_all_user_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        if result:
            # convert to correct pydantic model
            result.result = EarnedRolesModel.parse_obj(result.result)
        return result

    async def get_missing(self) -> BackendResult:
        """Get the users missing roles in the guild"""

        result = await self._backend_request(
            method="GET",
            route=destiny_role_get_missing_user_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        if result:
            # convert to correct pydantic model
            result.result = MissingRolesModel.parse_obj(result.result)
        return result

    async def get_detail(self, role: Role) -> BackendResult:
        """Get the details for the users role completion"""

        result = await self._backend_request(
            method="GET",
            route=destiny_role_get_user_route.format(
                guild_id=self.discord_guild.id, role_id=role.id, discord_id=self.discord_member.id
            ),
        )

        if result:
            # convert to correct pydantic model
            result.result = EarnedRoleModel.parse_obj(result.result)
        return result
