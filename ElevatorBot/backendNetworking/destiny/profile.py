from __future__ import annotations

import dataclasses
from typing import Optional

from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    destiny_profile_delete_route,
    destiny_profile_from_destiny_id_route,
    destiny_profile_from_discord_id_route,
    destiny_profile_has_token_route,
    destiny_profile_registration_role_route,
)

from NetworkingSchemas.destiny.profile import DestinyHasTokenModel, DestinyProfileModel


@dataclasses.dataclass
class DestinyProfile(BaseBackendConnection):
    """Get basic destiny information (discord_member, destiny_id, system)"""

    
    discord_member: Member
    discord_guild: Guild

    async def from_destiny_id(self, destiny_id: int) -> Optional[DestinyProfileModel]:
        """Get the destiny profile with a destiny_id"""

        # query the backend
        result = await self._backend_request(
            method="GET", route=destiny_profile_from_destiny_id_route.format(destiny_id=destiny_id)
        )

        # check if that id exists
        if not result:
            result.error_message = {"destiny_id": destiny_id}
            await self.send_error(result=result)
            return

        # check if the discord member is actually found
        discord_member = self.discord_guild.get_member(result.result["discord_id"])
        if not discord_member:
            result.error = "DestinyIdNotFound"
            result.error_message = {"destiny_id": destiny_id}
            await self.send_error(result=result)
            return

        # convert to correct pydantic model
        return DestinyProfileModel.parse_obj(result.result) if result else None

    async def from_discord_member(self) -> Optional[DestinyProfileModel]:
        """Get the destiny profile with a discord member object"""

        # query the backend
        result = await self._backend_request(
            method="GET", route=destiny_profile_from_discord_id_route.format(discord_id=self.discord_member.id)
        )

        # convert to correct pydantic model
        return DestinyProfileModel.parse_obj(result.result) if result else None

    async def has_token(self) -> Optional[DestinyHasTokenModel]:
        """Does the user have a working token"""

        self.hidden = True
        result = await self._backend_request(
            method="GET", route=destiny_profile_has_token_route.format(discord_id=self.discord_member.id)
        )

        # convert to correct pydantic model
        return DestinyHasTokenModel.parse_obj(result.result) if result else None

    async def assign_registration_role(self) -> bool:
        """Assign the user the registration role"""

        result = await self._backend_request(
            method="GET",
            route=destiny_profile_registration_role_route.format(
                discord_id=self.discord_member.id, guild_id=self.discord_guild.id
            ),
        )

        # returns EmptyResponseModel
        return bool(result)

    async def delete(self) -> bool:
        """Delete the profile"""

        result = await self._backend_request(
            method="DELETE", route=destiny_profile_delete_route.format(discord_id=self.discord_member.id)
        )

        # returns EmptyResponseModel
        return bool(result)
