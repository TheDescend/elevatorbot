from ElevatorBot.backgroundEvents.base import BaseEvent
from ElevatorBot.discordEvents.base import ElevatorSnake
from ElevatorBot.misc.cache import descend_cache
from ElevatorBot.static.descendOnlyIds import descend_channels


class MemberCountUpdater(BaseEvent):
    """This updates the member count for descend"""

    def __init__(self):
        interval_minutes = 30
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self, client: ElevatorSnake):
        # get the channel if exists and update that message
        try:
            channel = await descend_cache.get_member_count()
        except LookupError:
            return

        # update the name
        await channel.edit(
            name=f"𝖬𝖾𝗆𝖻𝖾𝗋𝗌｜{descend_channels.guild.member_count}",
            reason="Member Count Update",
        )
