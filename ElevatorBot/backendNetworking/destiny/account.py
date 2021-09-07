import dataclasses

import discord

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import destiny_account_name_route, destiny_account_solos_route


@dataclasses.dataclass
class DestinyAccount(BaseBackendConnection):
    client: discord.Client
    discord_member: discord.Member
    discord_guild: discord.Guild

    async def get_destiny_name(self) -> BackendResult:
        """Return the destiny name"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_name_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id)
        )

        # if no errors occurred, format the message
        if not result:
            result.error_message = {"discord_member": self.discord_member}

        return result

    async def get_solos(self) -> BackendResult:
        """Return the solos the user has done"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_solos_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id)
        )

        # if no errors occurred, format the message
        if not result:
            result.error_message = {"discord_member": self.discord_member}

        return result
