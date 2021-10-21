import dataclasses

from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import (
    elevator_servers_add,
    elevator_servers_delete,
)


@dataclasses.dataclass
class ElevatorGuilds(BaseBackendConnection):
    discord_guild: Guild
    discord_member: Member = dataclasses.field(init=False, default=None)

    async def add(self) -> BackendResult:
        """Add the guild"""

        return await self._backend_request(
            method="POST", route=elevator_servers_add.format(guild_id=self.discord_guild.id)
        )

    async def delete(self) -> BackendResult:
        """Delete the guild"""

        return await self._backend_request(
            method="DELETE", route=elevator_servers_delete.format(guild_id=self.discord_guild.id)
        )
