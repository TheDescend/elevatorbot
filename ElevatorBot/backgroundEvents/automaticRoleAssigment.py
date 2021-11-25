import asyncio

from dis_snek.client import Snake

from ElevatorBot.backgroundEvents.base import BaseEvent
from ElevatorBot.core.destiny.roles import Roles


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

    async def run(self, client: Snake):
        # loop through all guilds
        for guild in client.guilds:
            # gather the members
            await asyncio.gather(
                *[Roles(client=client, guild=guild, member=member, ctx=None).update() for member in guild.members]
            )
