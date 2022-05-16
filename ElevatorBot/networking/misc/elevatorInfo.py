import dataclasses
from typing import Optional

from naff import Guild, Member

from ElevatorBot.networking.http import BaseBackendConnection
from ElevatorBot.networking.routes import elevator_servers_add, elevator_servers_delete, elevator_servers_get
from Shared.networkingSchemas import ElevatorGuildsModel


@dataclasses.dataclass
class ElevatorGuilds(BaseBackendConnection):
    discord_guild: Optional[Guild]
    discord_member: Member = dataclasses.field(init=False, default=None)

    async def add(self):
        """Add the guild"""

        await self._backend_request(method="POST", route=elevator_servers_add.format(guild_id=self.discord_guild.id))

    async def delete(self, guild_id: int):
        """Delete the guild"""

        await self._backend_request(
            method="DELETE",
            route=elevator_servers_delete.format(guild_id=guild_id),
        )

    async def get(self) -> ElevatorGuildsModel:
        """Get Guild Data"""

        result = await self._backend_request(method="GET", route=elevator_servers_get)

        # convert to correct pydantic model
        return ElevatorGuildsModel.parse_obj(result.result)
