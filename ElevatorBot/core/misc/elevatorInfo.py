import dataclasses

import discord

from ElevatorBot.core.http import BaseBackendConnection
from ElevatorBot.core.routes import elevator_servers_add, elevator_servers_delete


@dataclasses.dataclass
class ElevatorGuilds(BaseBackendConnection):
    discord_guild: discord.Guild

    async def add(self):
        """Add the guild"""

        await self.backend_session.post(url=elevator_servers_add.format(guild_id=self.discord_guild.id))

    async def delete(
        self,
    ):
        """Delete the guild"""

        await self.backend_session.delete(url=elevator_servers_delete.format(guild_id=self.discord_guild.id))
