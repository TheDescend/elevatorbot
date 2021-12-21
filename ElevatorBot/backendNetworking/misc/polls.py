import dataclasses
from typing import Optional

from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    polls_delete_all_route,
    polls_delete_option_route,
    polls_delete_route,
    polls_get_route,
    polls_insert_route,
    polls_user_input_route,
)
from NetworkingSchemas.misc.polls import PollSchema


@dataclasses.dataclass()
class BackendPolls(BaseBackendConnection):
    guild: Optional[Guild]
    discord_member: Optional[Member]

    async def insert(self, name: str, description: str, channel_id: int, message_id: int) -> Optional[PollSchema]:
        """Insert a poll"""

        result = await self._backend_request(
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

        # convert to correct pydantic model
        return PollSchema.parse_obj(result.result) if result else None

    async def get(self, poll_id: int) -> Optional[PollSchema]:
        """Gets a poll"""

        result = await self._backend_request(
            method="GET",
            route=polls_get_route.format(guild_id=self.guild.id, discord_id=self.discord_member.id, poll_id=poll_id),
        )

        # convert to correct pydantic model
        return PollSchema.parse_obj(result.result) if result else None

    async def user_input(self, poll_id: int, choice_name: str) -> Optional[PollSchema]:
        """Handles a user input on a poll"""

        result = await self._backend_request(
            method="POST",
            route=polls_user_input_route.format(
                guild_id=self.guild.id, discord_id=self.discord_member.id, poll_id=poll_id
            ),
            data={"choice_name": choice_name},
        )

        # convert to correct pydantic model
        return PollSchema.parse_obj(result.result) if result else None

    async def remove_option(self, poll_id: int, choice_name: str) -> Optional[PollSchema]:
        """Remove an option from the db"""

        result = await self._backend_request(
            method="DELETE",
            route=polls_delete_option_route.format(
                guild_id=self.guild.id, discord_id=self.discord_member.id, poll_id=poll_id, option_name=choice_name
            ),
        )

        # convert to correct pydantic model
        return PollSchema.parse_obj(result.result) if result else None

    async def delete(self, poll_id: int) -> Optional[PollSchema]:
        """Delete a poll"""

        result = await self._backend_request(
            method="DELETE",
            route=polls_delete_route.format(guild_id=self.guild.id, discord_id=self.discord_member.id, poll_id=poll_id),
        )

        # convert to correct pydantic model
        return PollSchema.parse_obj(result.result) if result else None

    async def delete_all(self, guild_id: int) -> bool:
        """Deletes all polls for a guild"""

        result = await self._backend_request(
            method="DELETE",
            route=polls_delete_all_route.format(guild_id=guild_id),
        )

        # returns EmptyResponseModel
        return bool(result)
