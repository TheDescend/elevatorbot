from __future__ import annotations

import dataclasses

from dis_snek.client import Snake
from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import (
    destiny_profile_delete_route,
    destiny_profile_from_destiny_id_route,
    destiny_profile_from_discord_id_route,
    destiny_profile_has_token_route,
    destiny_profile_registration_role_route,
)
from ElevatorBot.static.schemas import DestinyData


@dataclasses.dataclass
class DestinyProfile(BaseBackendConnection):
    """Get basic destiny information (discord_member, destiny_id, system)"""

    client: Snake
    discord_member: Member
    discord_guild: Guild

    async def from_destiny_id(self, destiny_id: int) -> DestinyData | BackendResult:
        """Get the destiny profile with a destiny_id"""

        # query the backend
        result = await self._backend_request(
            method="GET", route=destiny_profile_from_destiny_id_route.format(destiny_id=destiny_id)
        )

        # check if that id exists
        if not result:
            result.error_message = {"destiny_id": destiny_id}
            return result

        # check if the discord member is actually found
        discord_member = self.discord_guild.get_member(result.result["discord_id"])
        if not discord_member:
            result.error = "DestinyIdNotFound"
            result.error_message = {"destiny_id": destiny_id}
            return result

        # set attributes
        return DestinyData(
            discord_member=discord_member,
            destiny_id=destiny_id,
            system=result.result["system"],
        )

    async def from_discord_member(self) -> DestinyData | BackendResult:
        """Get the destiny profile with a discord member object"""

        # query the backend
        result = await self._backend_request(
            method="GET", route=destiny_profile_from_discord_id_route.format(discord_id=self.discord_member.id)
        )

        # check if that id exists
        if not result:
            return result

        # set attributes
        return DestinyData(
            discord_member=self.discord_member,
            destiny_id=result.result["destiny_id"],
            system=result.result["system"],
        )

    async def has_token(self) -> bool:
        """Does the user have a working token"""

        result = await self._backend_request(
            method="GET", route=destiny_profile_has_token_route.format(discord_id=self.discord_member.id)
        )

        if result:
            return result.result["token"]
        return False

    async def assign_registration_role(self) -> BackendResult:
        """Assign the user the registration role"""

        result = await self._backend_request(
            method="GET",
            route=destiny_profile_registration_role_route.format(
                discord_id=self.discord_member.id, guild_id=self.discord_guild.id
            ),
        )

        # returns EmptyResponseModel
        return result

    async def delete(self) -> BackendResult:
        """Delete the profile"""

        result = await self._backend_request(
            method="DELETE", route=destiny_profile_delete_route.format(discord_id=self.discord_member.id)
        )

        # returns EmptyResponseModel
        return result
