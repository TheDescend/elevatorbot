from ElevatorBot.backgroundEvents.base import BaseEvent
from ElevatorBot.core.destiny.roles import Roles
from ElevatorBot.discordEvents.base import ElevatorSnake
from ElevatorBot.networking.destiny.profile import DestinyProfile


class AutomaticRoleAssignment(BaseEvent):
    """Every day, this updates all registered users roles"""

    def __init__(self):
        dow_day_of_week = "*"
        dow_hour = 1
        dow_minute = 0
        super().__init__(
            scheduler_type="cron",
            dow_day_of_week=dow_day_of_week,
            dow_hour=dow_hour,
            dow_minute=dow_minute,
        )

    async def run(self, client: ElevatorSnake):
        # loop through all guilds members
        for guild in client.guilds:
            for member in guild.humans:
                # ignore know unregistered people
                if await DestinyProfile(ctx=None, discord_member=member, discord_guild=guild).is_registered():
                    await Roles(guild=guild, member=member, ctx=None).update()
