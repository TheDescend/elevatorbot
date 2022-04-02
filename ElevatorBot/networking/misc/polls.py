import dataclasses
from typing import Optional

from dis_snek import Guild, Member

from ElevatorBot.networking.http import BaseBackendConnection
from ElevatorBot.networking.routes import (
    polls_delete_all_route,
    polls_delete_option_route,
    polls_delete_route,
    polls_get_route,
    polls_insert_route,
    polls_user_input_route,
)
from Shared.networkingSchemas.misc.polls import PollInsertSchema, PollSchema, PollUserInputSchema


@dataclasses.dataclass()
class BackendPolls(BaseBackendConnection):
    guild: Optional[Guild]
    discord_member: Optional[Member]

    async def insert(self, name: str, description: str, channel_id: int, message_id: int) -> PollSchema:
        """Insert a poll"""

        result = await self._backend_request(
            method="POST",
            route=polls_insert_route.format(guild_id=self.guild.id, discord_id=self.discord_member.id),
            data=PollInsertSchema(
                name=name,
                description=description,
                author_id=self.discord_member.id,
                guild_id=self.guild.id,
                channel_id=channel_id,
                message_id=message_id,
            ),
        )

        # convert to correct pydantic model
        return PollSchema.parse_obj(result.result)

    async def get(self, poll_id: int) -> PollSchema:
        """Gets a poll"""

        result = await self._backend_request(
            method="GET",
            route=polls_get_route.format(guild_id=self.guild.id, discord_id=self.discord_member.id, poll_id=poll_id),
        )

        # convert to correct pydantic model
        return PollSchema.parse_obj(result.result)

    async def user_input(self, poll_id: int, choice_name: str) -> PollSchema:
        """Handles a user input on a poll"""

        result = await self._backend_request(
            method="POST",
            route=polls_user_input_route.format(
                guild_id=self.guild.id, discord_id=self.discord_member.id, poll_id=poll_id
            ),
            data=PollUserInputSchema(choice_name=choice_name),
        )

        # convert to correct pydantic model
        return PollSchema.parse_obj(result.result)

    async def remove_option(self, poll_id: int, choice_name: str) -> PollSchema:
        """Remove an option from the db"""

        result = await self._backend_request(
            method="DELETE",
            route=polls_delete_option_route.format(
                guild_id=self.guild.id, discord_id=self.discord_member.id, poll_id=poll_id, option_name=choice_name
            ),
        )

        # convert to correct pydantic model
        return PollSchema.parse_obj(result.result)

    async def delete(self, poll_id: int) -> PollSchema:
        """Delete a poll"""

        result = await self._backend_request(
            method="DELETE",
            route=polls_delete_route.format(guild_id=self.guild.id, discord_id=self.discord_member.id, poll_id=poll_id),
        )

        # convert to correct pydantic model
        return PollSchema.parse_obj(result.result)

    async def delete_all(self, guild_id: int):
        """Deletes all polls for a guild"""

        await self._backend_request(
            method="DELETE",
            route=polls_delete_all_route.format(guild_id=guild_id),
        )
