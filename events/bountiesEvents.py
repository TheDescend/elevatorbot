import asyncio
import datetime
import json
import os
import pickle
from copy import deepcopy

import discord

from events.base_event import BaseEvent
from functions.bounties.bountiesBackend import getGlobalVar
from functions.bounties.bountiesFunctions import bountyCompletion, awardCompetitionBountiesPoints, bountiesFormatting, \
    displayBounties, updateAllExperience

# check if players have completed a bounty
from functions.bounties.bountiesTournament import tournamentRegistrationMessage
from functions.bounties.boutiesBountyRequirements import bounties_dict, competition_bounties_dict
from functions.database import getBountyUserList
from functions.persistentMessages import botStatus


class CheckBountyCompletion(BaseEvent):
    def __init__(self):
        interval_minutes = 30  # Set the interval for this event
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self, client):
        await bountyCompletion(client)

        # update the status
        await botStatus(client, "Bounties - Completion Update", datetime.datetime.now(tz=datetime.timezone.utc))


class GenerateBounties(BaseEvent):
    def __init__(self):
        # Set the interval for this event
        dow_day_of_week = "mon"
        dow_hour = 0
        dow_minute = 0
        super().__init__(scheduler_type="cron", dow_day_of_week=dow_day_of_week, dow_hour=dow_hour, dow_minute=dow_minute)

    async def run(self, client):
        # award points for the competition bounties
        await awardCompetitionBountiesPoints(client)

        # clean the tourn channel registration message if exist
        file = getGlobalVar()
        for guild in client.guilds:
            if guild.id == file["guild_id"]:
                try:
                    tourn_channel = discord.utils.get(guild.channels, id=file["tournament_channel"])
                    tourn_msg = await tourn_channel.fetch_message(file["tournament_channel_message_id"])
                    await tourn_msg.delete()
                except:
                    pass

        # looping though the bounties
        copy_of_bounty_dict = deepcopy(bounties_dict)
        file = {}
        file["bounties"] = {}
        for topic in copy_of_bounty_dict.keys():
            file["bounties"][topic] = {}
            for experience in copy_of_bounty_dict[topic].keys():
                ret = await bountiesFormatting(client, topic, copy_of_bounty_dict[topic][experience], amount_of_bounties=2)
                file["bounties"][topic][experience] = {}

                for key in ret:
                    value = ret[key]
                    file["bounties"][topic][experience][key] = value

        # looping though the competition bounties
        copy_of_competition_bounties_dict = deepcopy(competition_bounties_dict)
        file["competition_bounties"] = {}
        for topic in copy_of_competition_bounties_dict.keys():
            ret = await bountiesFormatting(client, topic, copy_of_competition_bounties_dict[topic])
            file["competition_bounties"][topic] = {}

            for key in ret:
                value = ret[key]
                file["competition_bounties"][topic][key] = value

                # if "tournament" is in there, put the tourn message up
                if "tournament" in value["requirements"]:
                    await tournamentRegistrationMessage(client)

        # add current time to list
        file["time"] = str(datetime.datetime.now())

        # overwrite the old bounties
        with open('functions/bounties/currentBounties.pickle', "wb+") as f:
            pickle.dump(file, f)

        print("Generated new bounties:")
        print(json.dumps(file, indent=4))

        # update the display
        task = displayBounties(client)
        asyncio.run_coroutine_threadsafe(task, client.loop)

        # delete old bounty completion tracking pickle
        if os.path.exists('functions/bounties/playerBountyStatus.pickle'):
            os.remove('functions/bounties/playerBountyStatus.pickle')

        # update the status
        await botStatus(client, "Bounties - Generation", datetime.datetime.now(tz=datetime.timezone.utc))


class UpdateExperienceLevels(BaseEvent):
    def __init__(self):
        # Set the interval for this event
        dow_day_of_week = "sun"
        dow_hour = 0
        dow_minute = 0
        super().__init__(scheduler_type="cron", dow_day_of_week=dow_day_of_week, dow_hour=dow_hour, dow_minute=dow_minute)

    async def run(self, client):
        for user in getBountyUserList():
            await updateAllExperience(client, user)
        print("Done updating experience")

        # update the status
        await botStatus(client, "Bounties - Experience Update", datetime.datetime.now(tz=datetime.timezone.utc))
