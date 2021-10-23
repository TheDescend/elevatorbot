import dataclasses

from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import (
    persistent_messages_delete_route,
    persistent_messages_get_route,
    persistent_messages_upsert_route,
)


@dataclasses.dataclass()
class BackendPersistentMessages(BaseBackendConnection):
    guild: Guild
    message_name: str

    discord_member: Member = dataclasses.field(init=False, default=None)

    async def get(self) -> BackendResult:
        """Gets a persistent message"""

        return await self._backend_request(
            method="GET",
            route=persistent_messages_get_route.format(guild_id=self.guild.id, message_name=self.message_name),
        )

    async def upsert(self, channel_id: int, message_id: int = None) -> BackendResult:
        """Upserts a persistent message"""

        return await self._backend_request(
            method="POST",
            route=persistent_messages_upsert_route.format(guild_id=self.guild.id, message_name=self.message_name),
            data={"channel_id": channel_id, "message_id": message_id},
        )

    async def delete(self) -> BackendResult:
        """Deletes a persistent message"""

        return await self._backend_request(
            method="DELETE",
            route=persistent_messages_delete_route.format(guild_id=self.guild.id, message_name=self.message_name),
        )
