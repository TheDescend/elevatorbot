import feedparser

from Backend.backgroundEvents.base import BaseEvent
from Backend.crud import persistent_messages, rss_feed
from Backend.database.base import get_async_session
from Backend.networking.elevatorApi import ElevatorApi


class RssFeedChecker(BaseEvent):
    """Checks for new Bungie Articles"""

    def __init__(self):
        interval_minutes = 5
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self):
        async with get_async_session().begin() as db:
            feed = feedparser.parse("https://www.bungie.net/en/rss/News")

            # loop through the articles and check if they have been published
            to_publish = []
            for item in reversed(feed["entries"]):
                if not await rss_feed.get(db=db, item_id=item["id"]):
                    to_publish.append(item)
                else:
                    # dont need to re-check all of them every time
                    break

            if to_publish:
                # get all guilds that have subscribed
                subscribed_data = []
                for subscribed in await persistent_messages.get_all_name(db=db, message_name="rss"):
                    subscribed_data.append(
                        {
                            "guild_id": subscribed.guild_id,
                            "channel_id": subscribed.channel_id,
                        }
                    )

                # loop through the items to publish and do that
                elevator_api = ElevatorApi()
                for item in to_publish:
                    data = {
                        "message": item["link"],
                        "embed_title": None,
                        "embed_description": None,
                        "guilds": subscribed_data,
                    }

                    # send the payload to elevator
                    result = await elevator_api.post(
                        route_addition="/messages",
                        json=data,
                    )

                    # remove db entry if channel doesnt exist
                    if result:
                        if not result.content["success"]:
                            for error_guild in result.content["guilds"]:
                                await persistent_messages.delete(
                                    db=db, message_name="rss", guild_id=error_guild["guild_id"]
                                )

                    # save item in DB
                    await rss_feed.insert(db=db, item_id=item["id"])
