import dataclasses

import discord

from ElevatorBot.core.http import BaseBackendConnection
from ElevatorBot.core.results import BackendResult
from ElevatorBot.core.routes import (
    destiny_clan_get_members_route,
    destiny_clan_get_route,
    destiny_clan_invite_route,
    destiny_clan_link_route,
    destiny_clan_search_members_route,
    destiny_clan_unlink_route,
)


@dataclasses.dataclass
class DestinyClan(BaseBackendConnection):
    client: discord.Client
    discord_member: discord.Member
    discord_guild: discord.Guild

    async def get_clan(self) -> BackendResult:
        """Return the destiny clan"""

        pass

        result = await self._backend_get(
            route=destiny_clan_get_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id)
        )

        # if no errors occurred, format the message
        if not result:
            result.error_message = {"discord_member": self.discord_member}

        return result

    async def get_clan_members(self) -> BackendResult:
        """Return the destiny clan members"""

        result = await self._backend_get(
            route=destiny_clan_get_members_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            )
        )

        # if no errors occurred, format the message
        if not result:
            result.error_message = {"discord_member": self.discord_member}

        return result

    async def search_for_clan_members(self, search_phrase: str) -> BackendResult:
        """Return the destiny clan members which match the search term"""

        result = await self._backend_get(
            route=destiny_clan_search_members_route.format(
                guild_id=self.discord_guild.id,
                discord_id=self.discord_member.id,
                search_phrase=search_phrase,
            )
        )

        # if no errors occurred, format the message
        if not result:
            result.error_message = {"discord_member": self.discord_member}

        return result

    async def invite_to_clan(self, to_invite: discord.Member) -> BackendResult:
        """Return the destiny clan members which match the search term"""

        result = await self._backend_get(
            route=destiny_clan_invite_route.format(
                guild_id=self.discord_guild.id,
                discord_id=to_invite.id
            )
        )

        # if errors occurred, format the message
        if not result:
            result.error_message = {"discord_member": self.discord_member, "discord_member2": to_invite}

        return result

    async def link(
        self,
    ) -> BackendResult:
        """Link the discord guild to the destiny guild"""

        result = await self._backend_get(
            route=destiny_clan_link_route.format(
                guild_id=self.discord_guild.id,
                discord_id=self.discord_member.id,
            )
        )

        # if errors occurred, format the message
        if not result:
            result.error_message = {
                "discord_member": self.discord_member,
            }

        return result

    async def unlink(
        self,
    ) -> BackendResult:
        """Unlink the discord guild to the destiny guild"""

        result = await self._backend_get(
            route=destiny_clan_unlink_route.format(
                guild_id=self.discord_guild.id,
                discord_id=self.discord_member.id,
            )
        )

        # if errors occurred, format the message
        if not result:
            result.error_message = {
                "discord_member": self.discord_member,
            }

        return result
