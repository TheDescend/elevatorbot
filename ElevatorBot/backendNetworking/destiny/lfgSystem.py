import dataclasses

import discord

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import (
    destiny_lfg_create_route,
    destiny_lfg_delete_route,
    destiny_lfg_get_all_route,
    destiny_lfg_get_route,
    destiny_lfg_update_route,
)
from ElevatorBot.static.schemas import LfgInputData, LfgUpdateData


@dataclasses.dataclass
class DestinyLfgSystem(BaseBackendConnection):
    client: discord.Client
    discord_guild: discord.Guild
    discord_member = None

    async def get_all(self) -> BackendResult:
        """Gets all the lfg events and info belonging to the guild"""

        result = await self._backend_request(
            method="GET",
            route=destiny_lfg_get_all_route.format(guild_id=self.discord_guild.id),
        )

        return result

    async def get(self, lfg_id: int) -> BackendResult:
        """Gets the lfg info belonging to the lfg id and guild"""

        result = await self._backend_request(
            method="GET",
            route=destiny_lfg_get_route.format(guild_id=self.discord_guild.id, lfg_id=lfg_id),
        )

        return result

    async def update(
        self,
        lfg_id: int,
        discord_member: discord.Member,
        lfg_data: LfgUpdateData,
    ):
        """Updates the lfg info belonging to the lfg id and guild"""

        result = await self._backend_request(
            method="POST",
            route=destiny_lfg_update_route.format(
                guild_id=self.discord_guild.id, discord_id=discord_member.id, lfg_id=lfg_id
            ),
            data=lfg_data.__dict__,
        )

        # if no errors occurred, format the message
        if not result:
            result.error_message = {"discord_member": discord_member}

        return result

    async def create(self, discord_member: discord.Member, lfg_data: LfgInputData):
        """Inserts the lfg info and gives it a new id"""

        await self._backend_request(
            method="POST",
            route=destiny_lfg_create_route.format(guild_id=self.discord_guild.id, discord_id=discord_member.id),
            data=lfg_data.__dict__,
        )

    async def delete(self, discord_member: discord.Member, lfg_id: int) -> BackendResult:
        """Delete the lfg info belonging to the lfg id and guild"""

        result = await self._backend_request(
            method="DELETE",
            route=destiny_lfg_delete_route.format(
                guild_id=self.discord_guild.id, discord_id=discord_member.id, lfg_id=lfg_id
            ),
        )

        # if no errors occurred, format the message
        if not result:
            result.error_message = {"discord_member": discord_member}

        return result
