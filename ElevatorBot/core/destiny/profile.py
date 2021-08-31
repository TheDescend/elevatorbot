from __future__ import annotations

import dataclasses
from typing import Union

import discord

from ElevatorBot.core.http import BaseBackendConnection
from ElevatorBot.core.results import BackendResult
from ElevatorBot.core.routes import (
    destiny_profile_delete_route,
    destiny_profile_from_destiny_id_route,
    destiny_profile_from_discord_id_route,
)
from ElevatorBot.static.schemas import DestinyData


@dataclasses.dataclass
class DestinyProfile(BaseBackendConnection):
    """Get basic destiny information (discord_member, destiny_id, system)"""

    client: discord.Client
    discord_member: discord.Member
    discord_guild: discord.Guild

    async def from_destiny_id(self, destiny_id: int) -> Union[DestinyData, BackendResult]:
        """Get the destiny profile with a destiny_id"""

        # query the backend
        result = await self._backend_get(destiny_profile_from_destiny_id_route.format(destiny_id=destiny_id))

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

    async def from_discord_member(
        self,
    ) -> Union[DestinyData, BackendResult]:
        """Get the destiny profile with a discord member object"""

        # query the backend
        result = await self._backend_get(
            destiny_profile_from_discord_id_route.format(discord_id=self.discord_member.id)
        )

        # check if that id exists
        if not result:
            result.error_message = {"discord_member": self.discord_member}
            return result

        # set attributes
        return DestinyData(
            discord_member=self.discord_member,
            destiny_id=result.result["destiny_id"],
            system=result.result["system"],
        )

    async def delete(
        self,
    ) -> BackendResult:
        """Delete the profile"""

        result = await self._backend_delete(
            route=destiny_profile_delete_route.format(discord_id=self.discord_member.id)
        )

        # check if OK
        if not result:
            result.error_message = {"discord_member": self.discord_member}
        return result
