from contextlib import suppress

from bungio.error import InvalidAuthentication

from Backend.backgroundEvents.base import BaseEvent
from Backend.crud import discord_users
from Backend.database.base import acquire_db_session


# todo make sure its not needed anymore and then delete (updated in activity updater)
class TokenUpdater(BaseEvent):
    """Every week, this updates user tokens, so they don't have to re-register so much"""

    def __init__(self):
        dow_day_of_week = "sun"
        dow_hour = 4
        dow_minute = 0
        super().__init__(
            scheduler_type="cron",
            dow_day_of_week=dow_day_of_week,
            dow_hour=dow_hour,
            dow_minute=dow_minute,
        )

    async def run(self):
        async with acquire_db_session() as db:
            all_users = await discord_users.get_all(db=db)

            # loop through all users
            # no need to task group this. this can take time, it's fine
            for user in all_users:
                if auth := user.auth:
                    # get a working token aka update
                    with suppress(InvalidAuthentication):
                        await auth.refresh()
