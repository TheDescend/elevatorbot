import datetime
import json
import asyncio
import pandas

from events.base_event import BaseEvent
from functions.dataLoading import getTriumphsJSON, updateDB, updateMissingPcgr, updateManifest
from functions.database import getAllDestinyIDs, lookupDiscordID
from functions.network import getJSONfromURL, refresh_token, handleAndReturnToken
from functions.persistentMessages import botStatus


class UpdateManifest(BaseEvent):
    def __init__(self):
        # Set the interval for this event
        dow_day_of_week = "*"
        dow_hour = 0
        dow_minute = 0
        super().__init__(scheduler_type="cron", dow_day_of_week=dow_day_of_week, dow_hour=dow_hour, dow_minute=dow_minute)

    async def run(self, client):
        await updateManifest()

        # update the status
        await botStatus(client, "Manifest Update", datetime.datetime.now(tz=datetime.timezone.utc))


class updateActivityDB(BaseEvent):
    def __init__(self):
        # Set the interval for this event
        interval_minutes = 60
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self, client):
        """
        This runs hourly and updates all the users infos,
        that are in one of the servers the bot is in.
        """
        print("Start updating DB...")

        # get all users the bot shares a guild with
        shared_guild = []
        for guild in client.guilds:
            for members in guild.members:
                shared_guild.append(members.id)
        set(shared_guild)

        # loop though all ids
        destinyIDs = await getAllDestinyIDs()
        for destinyID in destinyIDs:
            discordID = await lookupDiscordID(destinyID)

            # check is user is in a guild with bot
            if discordID not in shared_guild:
                destinyIDs.remove(destinyID)

        # update all users
        await asyncio.gather(*[updateDB(destinyID) for destinyID in destinyIDs])
        print("Done updating DB")

        # try to get the missing pgcrs
        await updateMissingPcgr()

        # update the status
        await botStatus(client, "Database Update", datetime.datetime.now(tz=datetime.timezone.utc))


class TokenUpdater(BaseEvent):
    """ Every week, this updates user tokens, so they dont have to re-register so much """

    def __init__(self):
        # bot is running on est, that should give it enough time (reset is at 12pm there)
        dow_day_of_week = "fri"
        dow_hour = 0
        dow_minute = 0
        super().__init__(scheduler_type="cron", dow_day_of_week=dow_day_of_week, dow_hour=dow_hour, dow_minute=dow_minute)

    async def run(self, client):
        for user in client.users:
            await handleAndReturnToken(user.id)

        # update the status
        await botStatus(client, "Token Refresh", datetime.datetime.now(tz=datetime.timezone.utc))



