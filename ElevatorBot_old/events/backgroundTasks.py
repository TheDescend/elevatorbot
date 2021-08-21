import asyncio
import datetime

import discord

from ElevatorBot.events.baseEvent import BaseEvent
from ElevatorBot.core.dataLoading import updateMissingPcgr, updateManifest
from ElevatorBot.core.destinyPlayer import DestinyPlayer
from ElevatorBot.core.persistentMessages import bot_status
from ElevatorBot.networking.bungieAuth import handle_and_return_token


class UpdateManifest(BaseEvent):
    def __init__(self):
        # Set the interval for this event
        dow_day_of_week = "*"
        dow_hour = 3
        dow_minute = 0
        super().__init__(
            scheduler_type="cron",
            dow_day_of_week=dow_day_of_week,
            dow_hour=dow_hour,
            dow_minute=dow_minute,
        )

    async def run(self, client):
        await updateManifest()

        # _update the status
        await bot_status(
            client, "Manifest Update", datetime.datetime.now(tz=datetime.timezone.utc)
        )


class UpdateActivityDB(BaseEvent):
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
        to_update = []
        for guild in client.guilds:
            for member in guild.members:
                destiny_player = await DestinyPlayer.from_discord_id(member.id)

                # check if exists / already in list
                if destiny_player and destiny_player not in to_update:
                    to_update.append(destiny_player)

        # _update all users in a gather for zooms
        await asyncio.gather(
            *[destiny_player.update_activity_db() for destiny_player in to_update]
        )

        print("Done updating DB")

        # try to get the missing pgcrs
        await updateMissingPcgr()

        # _update the status
        await bot_status(
            client, "Database Update", datetime.datetime.now(tz=datetime.timezone.utc)
        )


class TokenUpdater(BaseEvent):
    """Every week, this updates user tokens, so they dont have to re-register so much"""

    def __init__(self):
        # bot is running on est, that should give it enough time (reset is at 12pm there)
        dow_day_of_week = "fri"
        dow_hour = 5
        dow_minute = 0
        super().__init__(
            scheduler_type="cron",
            dow_day_of_week=dow_day_of_week,
            dow_hour=dow_hour,
            dow_minute=dow_minute,
        )

    async def run(self, client):
        print("Starting to refresh Tokens...")

        for user in client.users:
            await handle_and_return_token(user.id)

        # _update the status
        await bot_status(
            client, "Token Refresh", datetime.datetime.now(tz=datetime.timezone.utc)
        )

        print("Done refreshing Tokens")
