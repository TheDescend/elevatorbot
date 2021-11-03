import dataclasses
from typing import Optional

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
from NetworkingSchemas.destiny.clan import (
    DestinyClanLink,
    DestinyClanMembersModel,
    DestinyClanModel,
)


@dataclasses.dataclass
class DestinyClan(BaseBackendConnection):
    client: Snake
    discord_guild: Guild

    async def get_clan(self) -> Optional[DestinyClanModel]:
        """Return the destiny clan"""

        result = await self._backend_request(
            method="GET",
            route=destiny_clan_get_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
        )

        # convert to correct pydantic model
        return DestinyClanModel.parse_obj(result.result) if result else None

    async def get_clan_members(self) -> Optional[DestinyClanMembersModel]:
        """Return the destiny clan members"""

        result = await self._backend_request(
            method="GET",
            route=destiny_clan_get_members_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return DestinyClanMembersModel.parse_obj(result.result) if result else None

    async def search_for_clan_members(self, search_phrase: str) -> Optional[DestinyClanMembersModel]:
        """Return the destiny clan members which match the search term"""

        result = await self._backend_request(
            method="GET",
            route=destiny_clan_search_members_route.format(
                guild_id=self.discord_guild.id,
                discord_id=self.discord_member.id,
                search_phrase=search_phrase,
            ),
        )

        # convert to correct pydantic model
        return DestinyClanMembersModel.parse_obj(result.result) if result else None

    async def invite_to_clan(self, to_invite: Member) -> bool:
        """Return the destiny clan members which match the search term"""

        result = await self._backend_request(
            method="GET",
            route=destiny_clan_invite_route.format(guild_id=self.discord_guild.id, discord_id=to_invite.id),
            discord_member2=to_invite,
        )

        # returns EmptyResponseModel
        return True if result else None

    async def link(self) -> Optional[DestinyClanLink]:
        """Link the discord guild to the destiny guild"""

        result = await self._backend_request(
            method="GET",
            route=destiny_clan_link_route.format(
                guild_id=self.discord_guild.id,
                discord_id=self.discord_member.id,
            ),
        )

        # convert to correct pydantic model
        return DestinyClanLink.parse_obj(result.result) if result else None

    async def unlink(self) -> Optional[DestinyClanLink]:
        """Unlink the discord guild to the destiny guild"""

        result = await self._backend_request(
            method="GET",
            route=destiny_clan_unlink_route.format(
                guild_id=self.discord_guild.id,
                discord_id=self.discord_member.id,
            ),
        )

        # convert to correct pydantic model
        return DestinyClanLink.parse_obj(result.result) if result else None
