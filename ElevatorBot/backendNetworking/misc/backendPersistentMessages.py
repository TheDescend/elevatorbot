import dataclasses
from typing import Optional

from dis_snek import Guild, Member

from ElevatorBot.backendNetworking.errors import BackendException
from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    persistent_messages_delete_all_route,
    persistent_messages_delete_route,
    persistent_messages_get_all_route,
    persistent_messages_get_route,
    persistent_messages_upsert_route,
)
from Shared.networkingSchemas.misc.persistentMessages import (
    PersistentMessage,
    PersistentMessageDeleteInput,
    PersistentMessages,
    PersistentMessageUpsert,
)


@dataclasses.dataclass()
class BackendPersistentMessages(BaseBackendConnection):
    guild: Optional[Guild]
    message_name: Optional[str]

    discord_member: Member = dataclasses.field(init=False, default=None)

    async def get(self) -> PersistentMessage:
        """Gets a persistent message"""
        if self.guild is None:
            raise BackendException()

        result = await self._backend_request(
            method="GET",
            route=persistent_messages_get_route.format(guild_id=self.guild.id, message_name=self.message_name),
        )

        # convert to correct pydantic model
        return PersistentMessage.parse_obj(result.result)

    async def get_all(self) -> PersistentMessages:
        """Gets all persistent messages for the guild"""

        if self.guild is None:
            raise BackendException()

        result = await self._backend_request(
            method="GET",
            route=persistent_messages_get_all_route.format(guild_id=self.guild.id),
        )

        # convert to correct pydantic model
        return PersistentMessages.parse_obj(result.result)

    async def upsert(self, channel_id: int, message_id: Optional[int] = None) -> PersistentMessage:
        """Upserts a persistent message"""

        result = await self._backend_request(
            method="POST",
            route=persistent_messages_upsert_route.format(guild_id=self.guild.id, message_name=self.message_name),
            data=PersistentMessageUpsert(channel_id=channel_id, message_id=message_id),
        )

        # convert to correct pydantic model
        return PersistentMessage.parse_obj(result.result)

    async def delete(
        self, message_name: Optional[str] = None, channel_id: Optional[int] = None, message_id: Optional[int] = None
    ):
        """Deletes a persistent message"""

        await self._backend_request(
            method="POST",
            route=persistent_messages_delete_route.format(guild_id=self.guild.id),
            data=PersistentMessageDeleteInput(message_name=message_name, channel_id=channel_id, message_id=message_id),
        )

    async def delete_all(self, guild_id: int):
        """Deletes all persistent messages for a guild"""

        await self._backend_request(
            method="DELETE",
            route=persistent_messages_delete_all_route.format(guild_id=guild_id),
        )
