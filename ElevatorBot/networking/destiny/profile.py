from __future__ import annotations

import dataclasses

from naff import Guild, Member

from ElevatorBot.misc.cache import registered_role_cache
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.errorCodesAndResponses import get_error_codes_and_responses
from ElevatorBot.networking.errors import BackendException
from ElevatorBot.networking.http import BaseBackendConnection
from ElevatorBot.networking.routes import (
    destiny_profile_delete_route,
    destiny_profile_from_destiny_id_route,
    destiny_profile_from_discord_id_route,
    destiny_profile_has_token_route,
    destiny_profile_registration_role_route,
)
from Shared.networkingSchemas.destiny.profile import DestinyHasTokenModel, DestinyProfileModel


@dataclasses.dataclass
class DestinyProfile(BaseBackendConnection):
    """Get basic destiny information (discord_member, destiny_id, system)"""

    discord_member: Member
    discord_guild: Guild

    async def from_destiny_id(self, destiny_id: int) -> DestinyProfileModel:
        """Get the destiny profile with a destiny_id"""

        # query the backend
        result = await self._backend_request(
            method="GET",
            route=destiny_profile_from_destiny_id_route.format(destiny_id=destiny_id),
            destiny_id=destiny_id,
        )

        # check if the discord member is actually found
        discord_member = await self.discord_guild.fetch_member(result.result["discord_id"])
        if not discord_member:
            error = "DestinyIdNotFound"
            await self.ctx.send(
                ephemeral=True,
                embeds=embed_message(
                    title="Error", description=get_error_codes_and_responses()[error].format(destiny_id=destiny_id)
                ),
            )
            raise BackendException(error)

        # convert to correct pydantic model
        return DestinyProfileModel.parse_obj(result.result)

    async def from_discord_member(self) -> DestinyProfileModel:
        """Get the destiny profile with a discord member object"""

        # query the backend
        result = await self._backend_request(
            method="GET", route=destiny_profile_from_discord_id_route.format(discord_id=self.discord_member.id)
        )

        # convert to correct pydantic model
        return DestinyProfileModel.parse_obj(result.result)

    async def is_registered(self) -> bool:
        """Checks if the user is registered"""

        # check in cache if the user is registered
        # check if they were registered in the last hour
        if registered_role_cache.is_registered(self.discord_member.id):
            return True
        try:
            # check their status with the backend
            result = await self.from_discord_member()

            # todo change back to look up tokens maybe. Need to fix the tokens getting deleted reugalraly tho
            # result = await self.has_token()
        except BackendException as e:
            if e.error in ["NoToken", "DiscordIdNotFound"]:
                return False
            else:
                raise e

        registered = (not hasattr(result, "token")) or result.token

        if registered:
            registered_role_cache.registered_users[self.discord_member.id] = True

        return registered

    async def has_token(self) -> DestinyHasTokenModel:
        """Does the user have a working token"""

        self.hidden = True
        result = await self._backend_request(
            method="GET", route=destiny_profile_has_token_route.format(discord_id=self.discord_member.id)
        )

        # convert to correct pydantic model
        return DestinyHasTokenModel.parse_obj(result.result)

    async def assign_registration_role(self):
        """Assign the user the registration role"""

        await self._backend_request(
            method="GET",
            route=destiny_profile_registration_role_route.format(
                discord_id=self.discord_member.id, guild_id=self.discord_guild.id
            ),
        )

    async def delete(self):
        """Delete the profile"""

        await self._backend_request(
            method="DELETE", route=destiny_profile_delete_route.format(discord_id=self.discord_member.id)
        )
