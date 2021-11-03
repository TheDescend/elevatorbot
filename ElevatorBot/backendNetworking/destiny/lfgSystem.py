import dataclasses
from typing import Optional

from dis_snek.client import Snake
from dis_snek.models import Guild, Member

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
from NetworkingSchemas.destiny.lfgSystem import AllLfgOutputModel, LfgOutputModel


@dataclasses.dataclass
class DestinyLfgSystem(BaseBackendConnection):
    client: Snake
    discord_guild: Guild
    discord_member: Member = dataclasses.field(init=False, default=None)

    async def get_all(self) -> Optional[AllLfgOutputModel]:
        """Gets all the lfg events and info belonging to the guild"""

        result = await self._backend_request(
            method="GET",
            route=destiny_lfg_get_all_route.format(guild_id=self.discord_guild.id),
        )

        # convert to correct pydantic model
        return AllLfgOutputModel.parse_obj(result.result) if result else None

    async def get(self, lfg_id: int) -> Optional[LfgOutputModel]:
        """Gets the lfg info belonging to the lfg id and guild"""

        result = await self._backend_request(
            method="GET",
            route=destiny_lfg_get_route.format(guild_id=self.discord_guild.id, lfg_id=lfg_id),
        )

        # convert to correct pydantic model
        return LfgOutputModel.parse_obj(result.result) if result else None

    async def update(
        self,
        lfg_id: int,
        discord_member: Member,
        lfg_data: LfgUpdateData,
    ) -> Optional[LfgOutputModel]:
        """Updates the lfg info belonging to the lfg id and guild"""

        result = await self._backend_request(
            method="POST",
            route=destiny_lfg_update_route.format(
                guild_id=self.discord_guild.id, discord_id=discord_member.id, lfg_id=lfg_id
            ),
            data=lfg_data.__dict__,
        )

        # convert to correct pydantic model
        return LfgOutputModel.parse_obj(result.result) if result else None

    async def create(self, discord_member: Member, lfg_data: LfgInputData) -> Optional[LfgOutputModel]:
        """Inserts the lfg info and gives it a new id"""

        result = self._backend_request(
            method="POST",
            route=destiny_lfg_create_route.format(guild_id=self.discord_guild.id, discord_id=discord_member.id),
            data=lfg_data.__dict__,
        )

        # convert to correct pydantic model
        return LfgOutputModel.parse_obj(result.result) if result else None

    async def delete(self, discord_member: Member, lfg_id: int) -> bool:
        """Delete the lfg info belonging to the lfg id and guild"""

        result = await self._backend_request(
            method="DELETE",
            route=destiny_lfg_delete_route.format(
                guild_id=self.discord_guild.id, discord_id=discord_member.id, lfg_id=lfg_id
            ),
        )

        # returns EmptyResponseModel
        return True if result else None
