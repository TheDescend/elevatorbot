import dataclasses

import discord

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import (
    destiny_account_characters_route,
    destiny_account_name_route,
    destiny_account_solos_route,
    destiny_account_stat_characters_route,
    destiny_account_stat_route,
)


@dataclasses.dataclass
class DestinyAccount(BaseBackendConnection):
    client: discord.Client
    discord_guild: discord.Guild
    discord_member = None

    async def get_destiny_name(self) -> BackendResult:
        """Return the destiny name"""

        return await self._backend_request(
            method="GET",
            route=destiny_account_name_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
        )

    async def get_solos(self) -> BackendResult:
        """Return the solos the user has done"""

        return await self._backend_request(
            method="GET",
            route=destiny_account_solos_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
        )

    async def get_character_info(self) -> BackendResult:
        """Return the character info"""

        return await self._backend_request(
            method="GET",
            route=destiny_account_characters_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

    async def get_stat(self, stat_name: str, stat_category: str = "allTime") -> BackendResult:
        """Return the stat value"""

        return await self._backend_request(
            method="GET",
            route=destiny_account_stat_route.format(
                guild_id=self.discord_guild.id,
                discord_id=self.discord_member.id,
                stat_category=stat_category,
                stat_name=stat_name,
            ),
        )

    async def get_stat_by_characters(self, stat_name: str, stat_category: str = "allTime") -> BackendResult:
        """Return the stat value by character"""

        return await self._backend_request(
            method="GET",
            route=destiny_account_stat_characters_route.format(
                guild_id=self.discord_guild.id,
                discord_id=self.discord_member.id,
                stat_category=stat_category,
                stat_name=stat_name,
            ),
        )
