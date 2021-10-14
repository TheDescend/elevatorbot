import dataclasses

from dis_snek.client import Snake
from dis_snek.models.discord_objects.guild import Guild
from dis_snek.models.discord_objects.role import Role

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import destiny_role_get_all_user_route
from ElevatorBot.backendNetworking.routes import destiny_role_get_user_route


@dataclasses.dataclass
class DestinyRoles(BaseBackendConnection):
    client: Snake
    discord_guild: Guild

    async def get(self) -> BackendResult:
        """Get the users roles in the guild"""

        return await self._backend_request(
            method="GET",
            route=destiny_role_get_all_user_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

    async def get_detail(self, role: Role) -> BackendResult:
        """Get the details for the users role completion"""

        return await self._backend_request(
            method="GET",
            route=destiny_role_get_user_route.format(
                guild_id=self.discord_guild.id, role_id=role.id, discord_id=self.discord_member.id
            ),
        )
