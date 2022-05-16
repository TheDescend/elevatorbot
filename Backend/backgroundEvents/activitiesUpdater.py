from anyio import create_task_group

from Backend.backgroundEvents.base import BaseEvent
from Backend.core.destiny.activities import DestinyActivities
from Backend.crud import discord_users
from Backend.database.base import acquire_db_session, is_test_mode
from Backend.database.models import DiscordUsers
from Shared.functions.helperFunctions import split_list


class ActivitiesUpdater(BaseEvent):
    """Check for Activity Updates 4 times a day"""

    def __init__(self):
        interval_minutes = 60 * 4
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self):
        async with acquire_db_session() as db:
            all_users = await discord_users.get_all(db=db)

            # when testing, make this only return our user where we have data
            if is_test_mode():
                all_users = [user for user in all_users if user.destiny_id == 444]

        # update them in anyio tasks
        # max 10 at the same time tho
        for chunk in split_list(all_users, 10):
            async with create_task_group() as tg:
                for user in chunk:
                    tg.start_soon(self.handle_user, user)

        # try to get the missing pgcr
        if all_users:
            async with acquire_db_session() as db:
                activities = DestinyActivities(db=db, user=all_users[0])
                await activities.update_missing_pgcr()

    @staticmethod
    async def handle_user(user: DiscordUsers):
        """Create a sessions for the user and handle their activities"""

        async with acquire_db_session() as db:
            # make sure they have a token
            if await discord_users.token_is_expired(user=user):
                return

            # update the activities
            activities = DestinyActivities(db=db, user=user)
            await activities.update_activity_db()
