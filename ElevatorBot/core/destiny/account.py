import dataclasses

import discord

from ElevatorBot.core.http import BaseBackendConnection
from ElevatorBot.core.results import BackendResult
from ElevatorBot.core.routes import destiny_name_route


@dataclasses.dataclass
class DestinyAccount(BaseBackendConnection):
    client: discord.Client
    discord_member: discord.Member
    discord_guild: discord.Guild

    async def get_destiny_name(self) -> BackendResult:
        """Return the destiny name"""

        result = await self._backend_get(
            route=destiny_name_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id)
        )

        # if no errors occurred, format the message
        if not result:
            result.error_message = {"discord_member": self.discord_member}

        return result
