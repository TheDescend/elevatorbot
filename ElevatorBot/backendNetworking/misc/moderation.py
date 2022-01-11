import dataclasses

from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import moderation_mute, moderation_warning
from Shared.NetworkingSchemas.misc.moderation import (
    ModerationAddModel,
    ModerationModel,
    ModerationsModel,
)


@dataclasses.dataclass
class Moderation(BaseBackendConnection):
    discord_guild: Guild
    discord_member: Member

    async def get_mutes(self) -> ModerationsModel:
        """Get all mutes"""

        result = await self._backend_request(
            method="GET",
            route=moderation_mute.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
        )

        # convert to correct pydantic model
        return ModerationsModel.parse_obj(result.result)

    async def add_mute(self, reason: str, duration_in_seconds: int, mod_discord_id: int) -> ModerationModel:
        """Add a mute"""

        result = await self._backend_request(
            method="POST",
            route=moderation_mute.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
            data=ModerationAddModel(
                reason=reason, duration_in_seconds=duration_in_seconds, mod_discord_id=mod_discord_id
            ),
        )

        # convert to correct pydantic model
        return ModerationModel.parse_obj(result.result)

    async def get_warnings(self) -> ModerationsModel:
        """Get all warnings"""

        result = await self._backend_request(
            method="GET",
            route=moderation_warning.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
        )

        # convert to correct pydantic model
        return ModerationsModel.parse_obj(result.result)

    async def add_warning(self, reason: str, mod_discord_id: int) -> ModerationModel:
        """Add a warning"""

        result = await self._backend_request(
            method="POST",
            route=moderation_warning.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
            data=ModerationAddModel(reason=reason, mod_discord_id=mod_discord_id),
        )

        # convert to correct pydantic model
        return ModerationModel.parse_obj(result.result)
