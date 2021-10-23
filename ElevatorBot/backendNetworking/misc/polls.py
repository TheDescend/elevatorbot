import dataclasses

from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import (
    persistent_messages_delete_route,
    persistent_messages_get_route,
    persistent_messages_upsert_route,
    polls_delete_option_route,
    polls_delete_route,
    polls_get_route,
    polls_insert_route,
    polls_user_input_route,
)


@dataclasses.dataclass()
class BackendPolls(BaseBackendConnection):
    guild: Guild
    discord_member: Member

    async def insert(self, name: str, description: str, channel_id: int, message_id: int) -> BackendResult:
        """Insert a poll"""

        return await self._backend_request(
            method="POST",
            route=polls_insert_route.format(guild_id=self.guild.id, discord_id=self.discord_member.id),
            data={
                "name": name,
                "description": description,
                "data": {},
                "author_id": self.discord_member.id,
                "guild_id": self.guild.id,
                "channel_id": channel_id,
                "message_id": message_id,
            },
        )

    async def get(self, poll_id: int) -> BackendResult:
        """Gets a poll"""

        return await self._backend_request(
            method="GET",
            route=polls_get_route.format(guild_id=self.guild.id, discord_id=self.discord_member.id, poll_id=poll_id),
        )

    async def user_input(self, poll_id: int, choice_name: str) -> BackendResult:
        """Handles a user input on a poll"""

        return await self._backend_request(
            method="POST",
            route=polls_user_input_route.format(
                guild_id=self.guild.id, discord_id=self.discord_member.id, poll_id=poll_id
            ),
            data={"choice_name": choice_name, "user_id": self.discord_member.id},
        )

    async def remove_option(self, poll_id: int, choice_name: str) -> BackendResult:
        """Remove an option from the db"""

        return await self._backend_request(
            method="DELETE",
            route=polls_delete_option_route.format(
                guild_id=self.guild.id, discord_id=self.discord_member.id, poll_id=poll_id, option_name=choice_name
            ),
        )

    async def delete(self, poll_id: int) -> BackendResult:
        """Delete a poll"""

        return await self._backend_request(
            method="DELETE",
            route=polls_delete_route.format(guild_id=self.guild.id, discord_id=self.discord_member.id, poll_id=poll_id),
        )
