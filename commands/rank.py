from commands.base_command  import BaseCommand
from functions.dataLoading import getStats, getProfile, getCharactertypeList, getCharacterList, \
    getAggregateStatsForChar, getGearPiece, getVault, getWeaponKills
from functions.database import lookupDiscordID, getToken
from functions.formating import embed_message
from functions.network import getJSONfromURL
from static.config import CLANID

import pandas
import asyncio
import random

from static.dict import metricRaidCompletion, raidHashes


class rank(BaseCommand):
    # shadows charleys rank command. Currently works with "totaltime", "maxpower"
    def __init__(self):
        # A quick description for the help message
        description = "Shadows various Charley leaderboards with only clan members shown. `!rank help` for current leaderboards"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        supported = [
            "totaltime",
            "maxpower",
            "vaultspace",
            "orbs",
            "meleekills",
            "superkills",
            "grenadekills",
            "deaths",
            "suicides",
            "kills",
            "raids",
            "raidtime",
            "mqkills",
            "reclusekills",
            "mtkills"
        ]

        if len(params) == 1:
            if params[0].lower() == "help":
                await message.channel.send(embed=embed_message(
                    "Info",
                    f"""Currently supported are: \n`{"`, `".join(sorted(supported))}`"""
                ))

            elif params[0].lower() in supported:
                async with message.channel.typing():
                    embed = await handle_users(client, params[0], message.author.display_name, message.guild)

                if embed:
                    await message.channel.send(embed=embed)


async def handle_users(client, stat, display_name, guild):
    # init DF. "stat_sort" is only here, since I want to save numbers fancy (1,000,000) and that is a string and not an int so sorting wont work
    data = pandas.DataFrame(columns=["member", "stat", "stat_sort"])

    # loop through the clan members
    clan_members = (await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"))["Response"]["results"]
    results = await asyncio.gather(*[handle_user(stat, member, guild) for member in clan_members])

    for ret in results:
        # add user to DF
        if ret:
            data = data.append({"member": ret[0], "stat": ret[1], "stat_sort": ret[2]}, ignore_index=True)

            # the flavor text of the leaderboard, fe "Top Clanmembers by D2 Total Time Logged In" for totaltime
            leaderboard_text = ret[3]
            # the flavor text the stat will have, fe. "hours" for totaltime
            stat_text = ret[4]
            # for some stats lower might be better
            sort_by_ascending = ret[5]

    # sort and prepare DF
    data.sort_values(by=["stat_sort"], inplace=True, ascending=sort_by_ascending)
    data.reset_index(drop=True, inplace=True)

    # calculate the data for the embed
    ranking = []
    found = False
    for index, row in data.iterrows():
        if len(ranking) < 12:
            # setting a flag if user is in list
            if row["member"] == display_name:
                found = True
                ranking.append(write_line(index + 1, f"""[{row["member"]}]""", stat_text, row["stat"]))
            else:
                ranking.append(write_line(index + 1, row["member"], stat_text, row["stat"]))

        # looping through rest until original user is found
        elif (len(ranking) >= 12) and (not found):
            # adding only this user
            if row["member"] == display_name:
                ranking.append("...")
                ranking.append(write_line(index + 1, row["member"], stat_text, row["stat"]))
                break

        else:
            break

    # make and return embed
    return embed_message(
        leaderboard_text,
        "\n".join(ranking)
    )

async def handle_user(stat, member, guild):
    destinyID = int(member["destinyUserInfo"]["membershipId"])
    discordID = lookupDiscordID(destinyID)
    sort_by_ascending = False

    # catch people that are in the clan but not in discord, shouldn't happen tho
    try:
        name = guild.get_member(discordID).display_name
    except:
        print(f"DestinyID {destinyID} isn't in discord but he is in clan")
        return None

    # get the stat that we are looking for
    if stat == "totaltime":
        leaderboard_text = "Top Clanmembers by D2 Total Time Logged In"
        stat_text = "Hours"

        # in hours
        json = await getStats(destinyID)
        result_sort = add_stats(json, "secondsPlayed") / 60 / 60
        result = f"{result_sort:,}"

    elif stat == "orbs":
        leaderboard_text = "Top Clanmembers by PvE Orbs Generated"
        stat_text = "Orbs"

        json = await getStats(destinyID)
        result_sort = add_stats(json, "orbsDropped", scope="pve")
        result = f"{result_sort:,}"

    elif stat == "meleekills":
        leaderboard_text = "Top Clanmembers by D2 PvE Meleekills"
        stat_text = "Kills"

        json = await getStats(destinyID)
        result_sort = add_stats(json, "weaponKillsMelee", scope="pve")
        result = f"{result_sort:,}"

    elif stat == "superkills":
        leaderboard_text = "Top Clanmembers by D2 PvE Superkills"
        stat_text = "Kills"

        json = await getStats(destinyID)
        result_sort = add_stats(json, "weaponKillsSuper", scope="pve")
        result = f"{result_sort:,}"

    elif stat == "grenadekills":
        leaderboard_text = "Top Clanmembers by D2 PvE Grenadekills"
        stat_text = "Kills"

        json = await getStats(destinyID)
        result_sort = add_stats(json, "weaponKillsGrenade", scope="pve")
        result = f"{result_sort:,}"

    elif stat == "deaths":
        leaderboard_text = "Top Clanmembers by D2 PvE Deaths"
        stat_text = "Deaths"

        json = await getStats(destinyID)
        result_sort = add_stats(json, "deaths", scope="pve")
        result = f"{result_sort:,}"

    elif stat == "suicides":
        leaderboard_text = "Top Clanmembers by D2 PvE Suicides"
        stat_text = "Suicides"

        json = await getStats(destinyID)
        result_sort = add_stats(json, "suicides", scope="pve")
        result = f"{result_sort:,}"

    elif stat == "kills":
        leaderboard_text = "Top Clanmembers by D2 PvE Kills"
        stat_text = "Kills"

        json = await getStats(destinyID)
        result_sort = add_stats(json, "kills", scope="pve")
        result = f"{result_sort:,}"

    elif stat == "maxpower":
        leaderboard_text = "Top Clanmembers by D2 Maximum Reported Power"
        stat_text = "Power"

        json = await getStats(destinyID)
        result_sort = int(json["mergedAllCharacters"]["merged"]["allTime"]["highestLightLevel"]["basic"]["value"])
        result = f"{result_sort:,}"

    elif stat == "vaultspace":
        if not getToken(discordID):
            return None

        leaderboard_text = "Top Clanmembers by D2 Vaultspace Used"
        stat_text = "Used Space"

        result_sort = len(await getVault(4611686018467765462))
        result = f"{result_sort:,}"

    elif stat == "raids":
        leaderboard_text = "Top Clanmembers by D2 Total Raid Completions"
        stat_text = "Total"

        json = await getProfile(destinyID, 1100)
        result_sort = 0
        for raid in metricRaidCompletion:
            result_sort += json["metrics"]["data"]["metrics"][str(raid)]["objectiveProgress"]["progress"]
        result = f"{result_sort:,}"

    elif stat == "raidtime":
        leaderboard_text = "Top Clanmembers by D2 Total Raid Time"
        stat_text = "Hours"

        # in hours
        result_sort = int((await add_activity_stats(destinyID, raidHashes, "activitySecondsPlayed")) / 60 / 60)
        result = f"{result_sort:,}"

    elif stat == "mqkills":
        if not getToken(discordID):
            return None

        leaderboard_text = "Top Clanmembers by D2 Midnight Coup Kills"
        stat_text = "Kills"

        result_sort = await getWeaponKills(destinyID, 1128225405)
        result = f"{result_sort:,}"

    elif stat == "mtkills":
        if not getToken(discordID):
            return None

        leaderboard_text = "Top Clanmembers by D2 Mountaintop Kills"
        stat_text = "Kills"

        result_sort = await getWeaponKills(destinyID, 3993415705)
        result = f"{result_sort:,}"

    elif stat == "reclusekills":
        if not getToken(discordID):
            return None

        leaderboard_text = "Top Clanmembers by D2 Recluse Kills"
        stat_text = "Kills"

        result_sort = await getWeaponKills(destinyID, 3354242550)
        result = f"{result_sort:,}"

    else:
        return

    return [name, result, result_sort, leaderboard_text, stat_text, sort_by_ascending]


def write_line(index, member, stat_text, stat):
    return f"{index}) **{member}** _({stat_text}: {stat})_"


def add_stats(json, stat, scope="all"):
    result_sort = 0
    if scope == "all":
        result_sort = int(json["mergedAllCharacters"]["merged"]["allTime"][stat]["basic"]["value"])
        try:
            result_sort += int(json["mergedDeletedCharacters"]["merged"]["allTime"][stat]["basic"]["value"])
        except:
            pass
    elif scope == "pve":
        result_sort = int(json["mergedAllCharacters"]["results"]["allPvE"]["allTime"][stat]["basic"]["value"])
        try:
            result_sort += int(json["mergedDeletedCharacters"]["results"]["allPvE"]["allTime"][stat]["basic"]["value"])
        except:
            pass
    elif scope == "pvp":
        result_sort = int(json["mergedAllCharacters"]["results"]["allPvP"]["allTime"][stat]["basic"]["value"])
        try:
            result_sort += int(json["mergedDeletedCharacters"]["results"]["allPvP"]["allTime"][stat]["basic"]["value"])
        except:
            pass
    return result_sort

# activities = [[id1,id2], [id1], [id1, id2, id3]]
async def add_activity_stats(destinyID, hashes, stat):
    result_sort = 0
    chars = await getCharacterList(destinyID)
    for characterID in chars[1]:
        aggregateStats = await getAggregateStatsForChar(destinyID, chars[0], characterID)

        try:
            for activities in aggregateStats["activities"]:
                found = False
                for hash in hashes:
                    if found:
                        break
                    for hashID in hash:
                        if hashID == activities["activityHash"]:
                            result_sort += int(activities["values"][stat]["basic"]["value"])
                            found = True
                            break
        except:
            pass

    return result_sort




