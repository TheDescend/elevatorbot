import dataclasses

from naff import Guild, Member

from ElevatorBot.networking.http import BaseBackendConnection
from ElevatorBot.networking.routes import giveaway_create, giveaway_get, giveaway_insert, giveaway_remove
from Shared.networkingSchemas.misc.giveaway import GiveawayModel


@dataclasses.dataclass
class BackendGiveaway(BaseBackendConnection):
    discord_guild: Guild
    discord_member: Member
    message_id: int

    async def get(self) -> GiveawayModel:
        """Get the giveaway"""

        result = await self._backend_request(
            method="GET",
            route=giveaway_get.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id, giveaway_id=self.message_id
            ),
        )

        # convert to correct pydantic model
        return GiveawayModel.parse_obj(result.result)

    async def create(self):
        """Create a giveaway"""

        await self._backend_request(
            method="POST",
            route=giveaway_create.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id, giveaway_id=self.message_id
            ),
        )

    async def insert(self) -> GiveawayModel:
        """Insert the user into the giveaway"""

        result = await self._backend_request(
            method="POST",
            route=giveaway_insert.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id, giveaway_id=self.message_id
            ),
        )

        # convert to correct pydantic model
        return GiveawayModel.parse_obj(result.result)

    async def remove(self, to_remove: int) -> GiveawayModel:
        """Remove the user from the giveaway"""

        result = await self._backend_request(
            method="POST",
            route=giveaway_remove.format(
                guild_id=self.discord_guild.id, discord_id=to_remove, giveaway_id=self.message_id
            ),
        )

        # convert to correct pydantic model
        return GiveawayModel.parse_obj(result.result)
