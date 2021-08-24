from ElevatorBot.database.database import get_persistent_message
from ElevatorBot.events.baseEvent import BaseEvent


class GetMemberCount(BaseEvent):
    """Updates the member count channel to show how many members are currently in it"""

    def __init__(self):
        interval_minutes = 30  # Set the interval for this event
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    async def run(self, client):
        # loop through all guilds, get the channel id if exists and _update that
        for guild in client.guilds:
            result = await get_persistent_message("memberCount", guild.id)
            if not result:
                continue
            channel = guild.get_channel(result[0])
            if not channel:
                continue

            # _update the name - font is "math sans" from "https://qaz.wtf/u/convert.cgi"
            await channel.edit(name=f"𝖬𝖾𝗆𝖻𝖾𝗋𝗌｜{guild.member_count}", reason="Member Count Update")


class GetBoosterCount(BaseEvent):
    """Updates the booster count channel to show how many members are currently in it"""

    def __init__(self):
        interval_minutes = 30  # Set the interval for this event
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    async def run(self, client):
        # loop through all guilds, get the channel id if exists and _update that
        for guild in client.guilds:
            result = await get_persistent_message("boosterCount", guild.id)
            if not result:
                continue
            channel = guild.get_channel(result[0])
            if not channel:
                continue

            # _update the name
            await channel.edit(
                name=f"𝖡𝗈𝗈𝗌𝗍𝖾𝗋𝗌｜{guild.premium_subscription_count}",
                reason="Booster Count Update",
            )
