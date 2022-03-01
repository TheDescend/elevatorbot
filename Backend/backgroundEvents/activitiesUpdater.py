from anyio import create_task_group

from Backend.backgroundEvents.base import BaseEvent
from Backend.core.destiny.activities import DestinyActivities
from Backend.crud import discord_users
from Backend.database.base import get_async_sessionmaker
from Backend.database.models import DiscordUsers
from Shared.functions.helperFunctions import split_list


class ActivitiesUpdater(BaseEvent):
    """Check for Activity Updates 4 times a day"""

    def __init__(self):
        interval_minutes = 60 * 4
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self):
        async with get_async_sessionmaker().begin() as db:
            all_users = await discord_users.get_all(db=db)

        registered_users = []

        # loop through all users
        user = None
        for user in all_users:
            # add them to a task list
            registered_users.append(self.handle_user(user=user))

        # update them in anyio tasks
        # max 10 at the same time tho
        for chunk in split_list(registered_users, 10):
            async with create_task_group() as tg:
                for func in chunk:
                    tg.start_soon(func)

        # try to get the missing pgcr
        if user:
            async with get_async_sessionmaker().begin() as db:
                activities = DestinyActivities(db=db, user=user)
                await activities.update_missing_pgcr()

    @staticmethod
    async def handle_user(user: DiscordUsers):
        """Create a sessions for the user and handle their activities"""

        async with get_async_sessionmaker().begin() as db:
            # make sure they have a token
            if await discord_users.token_is_expired(db=db, user=user):
                return

            # update the activities
            activities = DestinyActivities(db=db, user=user)
            await activities.update_activity_db()
