import logging

from naff import Member

from ElevatorBot.backgroundEvents.base import BaseEvent
from ElevatorBot.core.misc.persistentMessages import PersistentMessages
from ElevatorBot.discordEvents.base import ElevatorClient
from ElevatorBot.networking.destiny.clan import DestinyClan
from ElevatorBot.networking.errors import BackendException

logger = logging.getLogger("backgroundEvents")


class ClanRoleUpdater(BaseEvent):
    """This updates the clan members roles"""

    def __init__(self):
        interval_minutes = 60
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self, client: ElevatorClient):
        for guild in client.guilds:
            # get the linked clan role
            persistent_messages = PersistentMessages(ctx=None, guild=guild, message_name="clan_role")
            try:
                result = await persistent_messages.get()
            except BackendException:
                return

            if clan_role := await guild.fetch_role(result.channel_id):
                # get clan members
                destiny_clan = DestinyClan(ctx=None, discord_guild=guild)
                clan_members = await destiny_clan.get_clan_members()
                clan_members_discord_ids = [member.discord_id for member in clan_members.members if member.discord_id]

                # check all members
                member: Member
                for member in guild.humans:
                    if member.id not in clan_members_discord_ids:
                        if member.has_role(clan_role):
                            await member.remove_role(role=clan_role, reason="Destiny2 Clan Membership Update")
                            logger.info(f"Removed clan role from {member}")
                    else:
                        if not member.has_role(clan_role):
                            await member.add_role(role=clan_role, reason="Destiny2 Clan Membership Update")
                            logger.info(f"Added clan role to {member}")
