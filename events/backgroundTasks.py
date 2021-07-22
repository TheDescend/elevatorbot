import datetime
import asyncio

import discord

from events.base_event import BaseEvent
from functions.dataLoading import updateDB, updateMissingPcgr, updateManifest
from database.database import getAllDestinyIDs, lookupDiscordID, getLastUpdated, lookupSystem
from functions.network import handleAndReturnToken
from functions.persistentMessages import bot_status


class UpdateManifest(BaseEvent):
    def __init__(self):
        # Set the interval for this event
        dow_day_of_week = "*"
        dow_hour = 1
        dow_minute = 0
        super().__init__(scheduler_type="cron", dow_day_of_week=dow_day_of_week, dow_hour=dow_hour, dow_minute=dow_minute)

    async def run(self, client):
        await updateManifest()

        # update the status
        await bot_status(client, "Manifest Update", datetime.datetime.now(tz=datetime.timezone.utc))


class updateActivityDB(BaseEvent):
    def __init__(self):
        # Set the interval for this event
        interval_minutes = 60
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self, client: discord.Client):
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
        to_update = []
        destiny_ids = await getAllDestinyIDs()
        for destiny_id in destiny_ids:
            discord_id = await lookupDiscordID(destiny_id)

            # check is user is in a guild with bot
            if discord_id in shared_guild:
                # get system
                system = await lookupSystem(destiny_id)
                if not system:
                    continue

                # get last updated for the users
                entry_time = await getLastUpdated(destiny_id)
                to_update.append({
                    "destiny_id": destiny_id,
                    "system": system,
                    "entry_time": entry_time
                })

        # update all users
        await asyncio.gather(*[updateDB(destiny_id=user["destiny_id"], system=user["system"], entry_time=user["entry_time"]) for user in to_update])
        print("Done updating DB")

        # try to get the missing pgcrs
        await updateMissingPcgr()

        # update the status
        await bot_status(client, "Database Update", datetime.datetime.now(tz=datetime.timezone.utc))


class TokenUpdater(BaseEvent):
    """ Every week, this updates user tokens, so they dont have to re-register so much """

    def __init__(self):
        # bot is running on est, that should give it enough time (reset is at 12pm there)
        dow_day_of_week = "fri"
        dow_hour = 3
        dow_minute = 0
        super().__init__(scheduler_type="cron", dow_day_of_week=dow_day_of_week, dow_hour=dow_hour, dow_minute=dow_minute)

    async def run(self, client):
        print("Starting to refresh Tokens...")

        for user in client.users:
            await handleAndReturnToken(user.id)

        # update the status
        await bot_status(client, "Token Refresh", datetime.datetime.now(tz=datetime.timezone.utc))

        print("Done refreshing Tokens")


