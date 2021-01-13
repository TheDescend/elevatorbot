from commands.base_command import BaseCommand
from functions.dataLoading import getProfile, getCharacterList, getPlayersPastPVE
from functions.formating import embed_message
from functions.network import getJSONfromURL
from functions.miscFunctions import hasAdminOrDevPermissions
from static.config import CLANID

import datetime
import asyncio
import io
import aiohttp
import discord


class day1spam(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[Admin] Starts the raid announcer for day1 completions. Will announce in the same channel"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        if not await hasAdminOrDevPermissions(message):
            return

        # >>> CHANGE HERE FOR DIFFERENT DAY 1 HASHES <<<
        leaderboard_channel = 778993490981027881
        activity_triumph = 2699580344
        activity_triumph_encounters = {
            4132628245: "Encounter 1",
            4132628244: "Encounter 2",
            4132628247: "Encounter 3",
            4132628246: "the final Boss"
        }
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
        leaderboard_msg = None
        leaderboard_channel = client.get_channel(leaderboard_channel)

        finished_raid = {}
        finished_encounters = {}
        clan_members = (await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"))["Response"]["results"]
        for member in clan_members:
            destinyID = member['destinyUserInfo']['membershipId']
            finished_encounters[destinyID] = {}
            for encounter in activity_triumph_encounters:
                finished_encounters[destinyID][encounter] = 0

        # loop until raid race is done
        now = datetime.datetime.now(datetime.timezone.utc)
        while cutoff_time > now:
            # gets all online users. Returns list with tuples (name, destinyID)
            online = []
            for member in (await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"))["Response"]["results"]:
                if member['isOnline']:
                    online.append((member['destinyUserInfo']['LastSeenDisplayName'], member['destinyUserInfo']['membershipId']))

            # loops through all online users
            result = await asyncio.gather(*[look_for_completion(member, finished_raid, finished_encounters, activity_triumph, activity_triumph_encounters, channel) for member in online])
            for res in result:
                if res is not None:
                    # check if all encounters are complete and if so save that
                    all_done = True
                    for encounter, complete in finished_encounters[res[1]].items():
                        if complete == 0:
                            all_done = False
                            break
                    if all_done:
                        finished_raid[res] = datetime.datetime.now(datetime.timezone.utc)

            # update leaderboard message
            leaderboard_msg = await update_leaderboard(leaderboard_channel, leaderboard_msg, finished_raid, finished_encounters, activity_triumph_encounters, clan_members)

            # wait 1 min before checking again
            await asyncio.sleep(60)

            # set new now
            now = datetime.datetime.now(datetime.timezone.utc)
            print(f"Done with loop at {str(now)}")

        async with channel.typing():
            if finished_raid:
                # get total time spend in raid
                completions = []
                for member in finished_raid:
                    try:
                        name = member[0]
                        destinyID = member[1]

                        # loop though activities
                        time_spend = 0
                        kills = 0
                        deaths = 0
                        async for activity in getPlayersPastPVE(destinyID, mode=4):
                            if datetime.datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ") < start:
                                continue

                            if activity["activityDetails"]["directorActivityHash"] in activity_hashes:
                                time_spend += activity["values"]["activityDurationSeconds"]["basic"]["value"]
                                kills += activity["values"]["kills"]["basic"]["value"]
                                deaths += activity["values"]["deaths"]["basic"]["value"]

                        # write the fancy text
                        completions.append(f"""<:desc_circle_b:768906489464619008>**{name}** - Kills: *{int(kills):,}*, Deaths: *{int(deaths):,}*, Time: *{str(datetime.timedelta(seconds=time_spend))}*""")
                    except:
                        print(f"Failed member {name}")

                completion_text = "\n".join(completions)
                msg = f"""The raid race is over :(. But some clan members managed to get a completion!\n⁣\n<:desc_logo_b:768907515193720874> __**Completions:**__\n{completion_text}"""
            else:
                msg = "Sadly nobody here finished the raid in time, good luck next time!"

            embed = embed_message(
                "Raid Race Summary",
                msg
            )

            stats = await channel.send(embed=embed)
            await stats.pin()


async def look_for_completion(member, finished_raid, finished_encounters, activity_triumph, activity_triumph_encounters, channel):
    name = member[0]
    destinyID = member[1]

    if member not in finished_raid:
        try:
            records = await getProfile(destinyID, 900)
            record = records["profileRecords"]["data"]["records"][str(activity_triumph)]

            # check each encounter
            for encounter_hash, description in activity_triumph_encounters.items():
                for record_objective_hash in record["objectives"]:
                    if encounter_hash == record_objective_hash["objectiveHash"]:
                        # abort if user has already completed that encounter
                        if finished_encounters[destinyID][encounter_hash] == 0:
                            # check if is complete
                            if record_objective_hash["complete"]:
                                finished_encounters[destinyID][encounter_hash] = 1
                                await channel.send(f"**{name}** has completed {description} <:PeepoDPS:754785311489523754>")

            return member

        except:
            pass

async def update_leaderboard(leaderboard_channel, leaderboard_msg, finished_raid, finished_encounters, activity_triumph_encounters, clan_members):
    running_raid = {}

    # loop through clan members
    for member in clan_members:
        destinyID = member['destinyUserInfo']['membershipId']
        name = member['destinyUserInfo']['LastSeenDisplayName']

        # only check if member did not finish the raid. loop through their encounter completion
        if (name, destinyID) not in finished_raid:
            for encounter, complete in finished_encounters[destinyID].items():
                if complete == 1:
                    try:
                        running_raid[(name, destinyID)].append(activity_triumph_encounters[encounter])
                    except KeyError:
                        running_raid[(name, destinyID)] = [activity_triumph_encounters[encounter]]

    embed = embed_message(
        "Race for Worlds First / Day One"
    )

    if finished_raid:
        embed.add_field(name="⁣", value=f"__Finished:__", inline=False)

        sort = {k: v for k, v in sorted(finished_raid.items(), key=lambda item: item[1], reverse=False)}
        times = []
        names = []
        for key, value in sort.items():
            names.append(key[0])
            times.append(f"{value.day}/{value.month} - {value.hour}:{value.minute:02d} UTC")

        embed.add_field(name="Name", value="\n".join(names), inline=True)
        embed.add_field(name="Time", value="\n".join(times), inline=True)

    if running_raid:
        embed.add_field(name="⁣", value=f"__Running:__", inline=False)

        sort = {k: v for k, v in sorted(running_raid.items(), key=lambda item: len(item[1]), reverse=True)}
        done = []
        names = []
        for key, value in sort.items():
            names.append(key[0])
            done.append(", ". join(value))

        embed.add_field(name="Name", value="\n".join(names), inline=True)
        embed.add_field(name="Completed", value="\n".join(done), inline=True)

    if not leaderboard_msg:
        leaderboard_msg = await leaderboard_channel.send(embed=embed)
    else:
        await leaderboard_msg.edit(embed=embed)
    return leaderboard_msg
