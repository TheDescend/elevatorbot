import io

import aiohttp
import discord

from commands.base_command import BaseCommand
from functions.dataLoading import getStats, getProfile, getCharacterList, \
    getAggregateStatsForChar, getInventoryBucket, getWeaponKills, returnManifestInfo, searchArmory, getAllGear, \
    getItemDefinition, getArtifact, getCharacterGear, getCharacterGearAndPower, getPlayersPastPVE, getCharacterPastPVE
from functions.database import lookupDiscordID, getToken, lookupSystem
from functions.formating import embed_message
from functions.network import getJSONfromURL
from functions.roles import hasAdminOrDevPermissions
from static.config import CLANID
from static.dict import metricRaidCompletion, raidHashes

import datetime
import asyncio


class day1spam(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[Admin] Starts the raid announcer for day1 completions. Will announce in the same channel"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        if not await hasAdminOrDevPermissions(message):
            return

        # >>> CHANGE HERE FOR DIFFERENT DAY 1 HASHES <<<
        activity_metric = 954805812
        activity_hashes = [3976949817, 910380154]
        cutoff_time = datetime.datetime(2020, 11, 22, 18, 0, tzinfo=datetime.timezone.utc)
        image_url = "https://www.bungie.net/img/destiny_content/pgcr/europa-raid-deep-stone-crypt.jpg"
        activity_name = "Europa - Deep Stone Crypt"


        channel = message.channel
        await message.delete()

        # printing the raid image. Taken from data.destinysets.com
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    data = io.BytesIO(await resp.read())
                    await channel.send(f"__**{activity_name}**__")
                    await channel.send("My day one mode is now activated and I will (hopefully) inform about completions. \nGood luck to everyone competing, will see you on the other side.")
                    await channel.send(file=discord.File(data, f'raid_image.png'))

        start = datetime.datetime.now()  # Need that for calculating total time. this time without utc timezone since bungie return doesnt care about that
        finished_raid = []

        # loop until raid race is done
        now = datetime.datetime.now(datetime.timezone.utc)
        while cutoff_time > now:
            # gets all online users. Returns list with tuples (name, destinyID)
            online = []
            for member in (await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"))["Response"]["results"]:
                if member['isOnline']:
                    online.append((member['destinyUserInfo']['LastSeenDisplayName'], member['destinyUserInfo']['membershipId']))

            # loops through all online users
            result = await asyncio.gather(*[look_for_completion(member, finished_raid, activity_metric, channel) for member in online])
            for res in result:
                if res is not None:
                    finished_raid.append(res)

            # wait 1 min before checking again
            await asyncio.sleep(60)

            # set new now
            now = datetime.datetime.now(datetime.timezone.utc)

        async with channel.typing():
            if finished_raid:
                # get total time spend in raid
                completions = []
                for member in finished_raid:
                    name = member[0]
                    destinyID = member[1]
                    chars = (await getCharacterList(destinyID))[1]

                    # loop though activities
                    time_spend = 0
                    kills = 0
                    deaths = 0
                    for characterID in chars:
                        async for activity in getCharacterPastPVE(destinyID, characterID, mode=4):
                            if datetime.datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ") < start:
                                break

                            if activity["activityDetails"]["directorActivityHash"] in activity_hashes:
                                time_spend += activity["values"]["activityDurationSeconds"]["basic"]["value"]
                                kills += activity["values"]["kills"]["basic"]["value"]
                                deaths += activity["values"]["deaths"]["basic"]["value"]

                    # write the fancy text
                    completions.append(f"""<:desc_circle_b:768906489464619008>**{name}** - Kills: *{int(kills):,}*, Deaths: *{int(deaths):,}*, Time: *{str(datetime.timedelta(seconds=time_spend))}*""")

                completion_text = "\n".join(completions)
                msg = f"""The raid race is over :(. But some clan members managed to get a completion!\n⁣\n<:desc_logo_b:768907515193720874> __**Completions:**__\n{completion_text}"""
            else:
                msg = "Sadly nobody here finished the raid in time, good luck next time!"

            embed = embed_message(
                "Raid Race Summary",
                msg
            )

            await channel.send(embed=embed)


async def look_for_completion(member, finished_raid, activity_metric, channel):
    name = member[0]
    destinyID = member[1]

    if member not in finished_raid:
        try:
            metrics = await getProfile(destinyID, 1100)
            if metrics["metrics"]["data"]["metrics"][str(activity_metric)]["objectiveProgress"]["progress"] > 0:
                await channel.send(f"**{name}** has completed the raid. Congratulations! <:PeepoDPS:754785311489523754>")
                return member
        except:
            pass
