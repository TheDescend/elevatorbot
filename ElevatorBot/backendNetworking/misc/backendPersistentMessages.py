import dataclasses
from typing import Optional

from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import (
    persistent_messages_delete_route,
    persistent_messages_get_route,
    persistent_messages_upsert_route,
)
from NetworkingSchemas.misc.persistentMessages import PersistentMessage


@dataclasses.dataclass()
class BackendPersistentMessages(BaseBackendConnection):
    guild: Guild
    message_name: str

    discord_member: Member = dataclasses.field(init=False, default=None)

    async def get(self) -> Optional[PersistentMessage]:
        """Gets a persistent message"""

        result = await self._backend_request(
            method="GET",
            route=persistent_messages_get_route.format(guild_id=self.guild.id, message_name=self.message_name),
        )

        # convert to correct pydantic model
        return PersistentMessage.parse_obj(result.result) if result else None

    async def upsert(self, channel_id: int, message_id: int = None) -> Optional[PersistentMessage]:
        """Upserts a persistent message"""

        result = await self._backend_request(
            method="POST",
            route=persistent_messages_upsert_route.format(guild_id=self.guild.id, message_name=self.message_name),
            data={"channel_id": channel_id, "message_id": message_id},
        )

        # convert to correct pydantic model
        return PersistentMessage.parse_obj(result.result) if result else None

    async def delete(self) -> bool:
        """Deletes a persistent message"""

        result = await self._backend_request(
            method="DELETE",
            route=persistent_messages_delete_route.format(guild_id=self.guild.id, message_name=self.message_name),
        )

        # returns EmptyResponseModel
        return bool(result)
