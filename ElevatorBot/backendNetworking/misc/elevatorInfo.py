import dataclasses
from typing import Optional

from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    elevator_servers_add,
    elevator_servers_delete,
)


@dataclasses.dataclass
class ElevatorGuilds(BaseBackendConnection):
    discord_guild: Optional[Guild]
    discord_member: Member = dataclasses.field(init=False, default=None)

    async def add(self) -> bool:
        """Add the guild"""

        result = await self._backend_request(
            method="POST", route=elevator_servers_add.format(guild_id=self.discord_guild.id)
        )

        # returns EmptyResponseModel
        return bool(result)

    async def delete(self, guild_id: int) -> bool:
        """Delete the guild"""

        result = await self._backend_request(
            method="DELETE",
            route=elevator_servers_delete.format(guild_id=guild_id),
        )

        # returns EmptyResponseModel
        return bool(result)
