from Backend.backgroundEvents import BaseEvent
from Backend.crud import discord_users
from Backend.database.base import get_async_session
from Backend.networking.bungieAuth import BungieAuth


class TokenUpdater(BaseEvent):
    """Every week, this updates user tokens, so they dont have to re-register so much"""

    def __init__(self):
        dow_day_of_week = "mon"
        dow_hour = 4
        dow_minute = 0
        super().__init__(
            scheduler_type="cron",
            dow_day_of_week=dow_day_of_week,
            dow_hour=dow_hour,
            dow_minute=dow_minute,
        )

    async def run(self):
        async with get_async_session().begin() as db:
            all_users = await discord_users.get_all(db=db)

            # loop through all users
            # no need to gather. this can take time, its fine
            for user in all_users:
                if user.token:
                    auth = BungieAuth(db=db, user=user)

                    # get a working token aka update
                    await auth.get_working_token()