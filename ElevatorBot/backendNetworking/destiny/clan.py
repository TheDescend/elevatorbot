import dataclasses
from typing import Optional

from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    destiny_clan_get_members_no_cache_route,
    destiny_clan_get_members_route,
    destiny_clan_get_route,
    destiny_clan_invite_route,
    destiny_clan_kick_route,
    destiny_clan_link_route,
    destiny_clan_search_members_route,
    destiny_clan_unlink_route,
)

from NetworkingSchemas.destiny.clan import (
    DestinyClanLink,
    DestinyClanMembersModel,
    DestinyClanModel,
)
from NetworkingSchemas.destiny.profile import DestinyProfileModel


@dataclasses.dataclass
class DestinyClan(BaseBackendConnection):
    
    discord_guild: Guild

    discord_member: Member = dataclasses.field(init=False)

    async def get_clan(self) -> Optional[DestinyClanModel]:
        """Return the linked destiny clan"""

        result = await self._backend_request(
            method="GET",
            route=destiny_clan_get_route.format(guild_id=self.discord_guild.id),
        )

        # convert to correct pydantic model
        return DestinyClanModel.parse_obj(result.result) if result else None

    async def get_clan_members(self, use_cache: bool = True) -> Optional[DestinyClanMembersModel]:
        """Return the destiny clan members"""

        if use_cache:
            route = destiny_clan_get_members_route
        else:
            route = destiny_clan_get_members_no_cache_route
        result = await self._backend_request(
            method="GET",
            route=route.format(guild_id=self.discord_guild.id),
        )

        # convert to correct pydantic model
        return DestinyClanMembersModel.parse_obj(result.result) if result else None

    async def search_for_clan_members(self, search_phrase: str) -> Optional[DestinyClanMembersModel]:
        """Return the destiny clan members which match the search term"""

        result = await self._backend_request(
            method="GET",
            route=destiny_clan_search_members_route.format(
                guild_id=self.discord_guild.id,
                search_phrase=search_phrase,
            ),
        )

        # convert to correct pydantic model
        return DestinyClanMembersModel.parse_obj(result.result) if result else None

    async def invite_to_clan(self, to_invite: Member) -> Optional[DestinyProfileModel]:
        """Invite the user to the linked clan"""

        result = await self._backend_request(
            method="POST",
            route=destiny_clan_invite_route.format(guild_id=self.discord_guild.id, discord_id=to_invite.id),
        )

        # convert to correct pydantic model
        return DestinyProfileModel.parse_obj(result.result) if result else None

    async def kick_from_clan(self, to_kick: Member) -> Optional[DestinyProfileModel]:
        """Kick the user from the linked clan"""

        result = await self._backend_request(
            method="POST",
            route=destiny_clan_kick_route.format(guild_id=self.discord_guild.id, discord_id=to_kick.id),
        )

        # convert to correct pydantic model
        return DestinyProfileModel.parse_obj(result.result) if result else None

    async def link(self, linked_by: Member) -> Optional[DestinyClanLink]:
        """Link the discord guild to the destiny guild"""

        result = await self._backend_request(
            method="POST",
            route=destiny_clan_link_route.format(
                guild_id=self.discord_guild.id,
                discord_id=linked_by.id,
            ),
        )

        # convert to correct pydantic model
        return DestinyClanLink.parse_obj(result.result) if result else None

    async def unlink(self, unlinked_by: Member) -> Optional[DestinyClanLink]:
        """Unlink the discord guild to the destiny guild"""

        result = await self._backend_request(
            method="DELETE",
            route=destiny_clan_unlink_route.format(
                guild_id=self.discord_guild.id,
                discord_id=unlinked_by.id,
            ),
        )

        # convert to correct pydantic model
        return DestinyClanLink.parse_obj(result.result) if result else None
