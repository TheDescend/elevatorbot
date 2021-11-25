import dataclasses
from typing import Optional

from dis_snek.client import Snake
from dis_snek.models.discord_objects.guild import Guild
from dis_snek.models.discord_objects.role import Role

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    destiny_role_delete_all_route,
    destiny_role_delete_route,
    destiny_role_get_all_user_route,
    destiny_role_get_missing_user_route,
    destiny_role_get_user_route,
)
from ElevatorBot.misc.cache import registered_role_cache
from NetworkingSchemas.destiny.roles import (
    EarnedRoleModel,
    EarnedRolesModel,
    MissingRolesModel,
)


@dataclasses.dataclass
class DestinyRoles(BaseBackendConnection):
    client: Snake
    discord_guild: Optional[Guild]

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

    async def delete_all(self, guild_id: int) -> bool:
        """Delete all guild roles"""

        result = await self._backend_request(
            method="DELETE",
            route=destiny_role_delete_all_route.format(guild_id=guild_id),
        )

        if result:
            # reset the register role cache
            try:
                registered_role_cache.guild_to_role.pop(guild_id)
            except KeyError:
                pass

        # returns EmptyResponseModel
        return bool(result)

    async def delete(self, guild_id: int, role_id: int) -> bool:
        """Delete the specified role"""

        result = await self._backend_request(
            method="DELETE",
            route=destiny_role_delete_route.format(guild_id=guild_id, role_id=role_id),
        )

        if result:
            # reset the register role cache
            try:
                if registered_role_cache.guild_to_role[guild_id].id == role_id:
                    registered_role_cache.guild_to_role.pop(guild_id)
            except KeyError:
                pass

        # returns EmptyResponseModel
        return bool(result)
