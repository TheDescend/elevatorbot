import dataclasses

from dis_snek.models import Guild
from dis_snek.models import Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import elevator_servers_add
from ElevatorBot.backendNetworking.routes import elevator_servers_delete


@dataclasses.dataclass
class ElevatorGuilds(BaseBackendConnection):
    discord_guild: Guild
    discord_member: Member = dataclasses.field(init=False, default=None)

    async def add(self):
        """Add the guild"""

        await self._backend_request(method="POST", route=elevator_servers_add.format(guild_id=self.discord_guild.id))

    async def delete(
        self,
    ):
        """Delete the guild"""

        await self._backend_request(
            method="DELETE", route=elevator_servers_delete.format(guild_id=self.discord_guild.id)
        )
