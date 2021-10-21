import dataclasses

from dis_snek.client import Snake
from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import (
    destiny_clan_get_members_route,
    destiny_clan_get_route,
    destiny_clan_invite_route,
    destiny_clan_link_route,
    destiny_clan_search_members_route,
    destiny_clan_unlink_route,
)


@dataclasses.dataclass
class DestinyClan(BaseBackendConnection):
    client: Snake
    discord_guild: Guild

    async def get_clan(self) -> BackendResult:
        """Return the destiny clan"""

        return await self._backend_request(
            method="GET",
            route=destiny_clan_get_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
        )

    async def get_clan_members(self) -> BackendResult:
        """Return the destiny clan members"""

        return await self._backend_request(
            method="GET",
            route=destiny_clan_get_members_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

    async def search_for_clan_members(self, search_phrase: str) -> BackendResult:
        """Return the destiny clan members which match the search term"""

        return await self._backend_request(
            method="GET",
            route=destiny_clan_search_members_route.format(
                guild_id=self.discord_guild.id,
                discord_id=self.discord_member.id,
                search_phrase=search_phrase,
            ),
        )

    async def invite_to_clan(self, to_invite: Member) -> BackendResult:
        """Return the destiny clan members which match the search term"""

        result = await self._backend_request(
            method="GET",
            route=destiny_clan_invite_route.format(guild_id=self.discord_guild.id, discord_id=to_invite.id),
        )

        # if errors occurred, format the message
        if not result:
            result.error_message = {"discord_member": self.discord_member, "discord_member2": to_invite}

        return result

    async def link(self) -> BackendResult:
        """Link the discord guild to the destiny guild"""

        return await self._backend_request(
            method="GET",
            route=destiny_clan_link_route.format(
                guild_id=self.discord_guild.id,
                discord_id=self.discord_member.id,
            ),
        )

    async def unlink(self) -> BackendResult:
        """Unlink the discord guild to the destiny guild"""

        return await self._backend_request(
            method="GET",
            route=destiny_clan_unlink_route.format(
                guild_id=self.discord_guild.id,
                discord_id=self.discord_member.id,
            ),
        )
