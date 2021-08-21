import datetime

import discord
import feedparser

from ElevatorBot.database.database import rss_item_exist, rss_item_add
from ElevatorBot.events.baseEvent import BaseEvent
from ElevatorBot.core.persistentMessages import (
    get_persistent_message_or_channel,
    bot_status,
)


class RssFeedChecker(BaseEvent):
    """Will check for new Bungie Articles"""

    def __init__(self):
        # Set the interval for this event
        interval_minutes = 5
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self, client: discord.Client):
        feed = feedparser.parse("https://www.bungie.net/en/rss/News")

        # loop through the articles and check if they have been published
        for item in reversed(feed["entries"]):
            if not await rss_item_exist(item["id"]):
                # send message
                for guild in client.guilds:
                    rss_channel = await get_persistent_message_or_channel(
                        client, "rss", guild.id
                    )
                    if rss_channel:
                        await rss_channel.send(item["link"])

                # save item in DB
                await rss_item_add(item["id"])

        # _update the status
        await bot_status(
            client, "RSS Feed Check", datetime.datetime.now(tz=datetime.timezone.utc)
        )
