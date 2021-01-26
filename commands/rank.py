import asyncio

import pandas
import discord
from discord.ext.commands import MemberConverter

from commands.base_command import BaseCommand
from functions.dataLoading import getStats, getProfile, getCharacterList, \
    getAggregateStatsForChar, getInventoryBucket, getWeaponStats, returnManifestInfo, getAllGear, \
    getItemDefinition, getArtifact, getCharacterGear, getCharacterGearAndPower, getPlayersPastActivities, searchForItem
from functions.database import lookupDiscordID, getToken, lookupSystem
from functions.formating import embed_message
from functions.miscFunctions import show_help
from functions.network import getJSONfromURL
from static.config import CLANID
from static.dict import metricRaidCompletion, raidHashes


class rank(BaseCommand):
    # shadows charleys rank command. Currently works with "totaltime", "maxpower"

    supported = [
        "discordjoindate",
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
        "weapon",
        "weaponprecision",
        "weaponprecisionpercent",
        "armor",
        "enhancementcores",
        "forges",
        "afkforges",
    ]

    def __init__(self):
        # A quick description for the help message
        description = "Shadows various Charley leaderboards with only clan members shown. Use !rank help to get currently supported leaderboards"
        params = [f"leaderboard {'|'.join(sorted(self.supported))}"]
        topic = "Destiny"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        # show error msg if wrong args
        if params[0].lower() not in self.supported:
            await show_help(message, "rank", self.params)
            return

        item_name = None
        item_hashes = None
        if params[0].lower() in ["weapon", "weaponprecision", "weaponprecisionpercent"]:
            if len(params) == 1:
                await message.channel.send(embed=embed_message(
                    "Info",
                    "Please specify a weapon"
                ))
                return

            else:
                item_name, item_hashes = await searchForItem(client, message, " ".join(params[1:]))
                if not item_name:
                    return

        elif params[0].lower() == "armor":
            stats = {
                "mobility": 2996146975,
                "resilience": 392767087,
                "recovery": 1943323491,
                "discipline": 1735777505,
                "intellect": 144602215,
                "strength": 4244567218
            }

            if len(params) == 1 or params[1] not in stats:
                await message.channel.send(embed=embed_message(
                    "Info",
                    f"""Please specify a stat, available are: \n`{"`, `".join(list(stats.keys()))}`"""
                ))
                return

            else:
                item_name = params[1]
                item_hashes = stats[item_name]

        async with message.channel.typing():
            embed = await handle_users(client, params[0].lower(), mentioned_user.display_name, message.guild, item_hashes, item_name)

        if embed:
            await message.channel.send(embed=embed)


async def handle_users(client, stat, display_name, guild, extra_hash, extra_name):
    # init DF. "stat_sort" is only here, since I want to save numbers fancy (1,000,000) and that is a string and not an int so sorting wont work
    data = pandas.DataFrame(columns=["member", "stat", "stat_sort"])

    # loop through the clan members
    clan_members = (await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"))["Response"]["results"]
    results = await asyncio.gather(*[handle_user(stat, member, guild, extra_hash, extra_name) for member in clan_members])
    if len(results) < 1:
        return embed_message(
            "Error",
            "No users found"
        )
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

async def handle_user(stat, member, guild, extra_hash, extra_name):
    destinyID = int(member["destinyUserInfo"]["membershipId"])
    discordID = lookupDiscordID(destinyID)
    sort_by_ascending = False

    if not getToken(discordID):
        return None

    # catch people that are in the clan but not in discord, shouldn't happen tho
    try:
        discord_member = guild.get_member(discordID)
        name = discord_member.display_name
    except:
        print(f"DestinyID {destinyID} isn't in discord but he is in clan")
        return None

    # get the stat that we are looking for
    if stat == "discordjoindate":
        sort_by_ascending = True
        leaderboard_text = "Top Clanmembers by Discord Join Date"
        stat_text = "Date"

        result_sort = discord_member.joined_at
        result = discord_member.joined_at.strftime("%d/%m/%Y, %H:%M")

    elif stat == "totaltime":
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
        #TODO efficiency
        if not getToken(discordID):
            return None

        leaderboard_text = "Top Clanmembers by D2 Maximum Reported Power"
        stat_text = "Power"

        artifact_power = (await getArtifact(destinyID))["powerBonus"]
        system = lookupSystem(destinyID)

        items = await getCharacterGearAndPower(destinyID)
        items = sort_gear_by_slot(items)

        results = await asyncio.gather(*[get_highest_item_light_level(destinyID, system, slot) for slot in items])

        total_power = 0
        for ret in results:
            total_power += ret
        total_power /= 8

        result_sort = int(total_power + artifact_power)
        result = f"{int(total_power):,} + {artifact_power:,}"

    elif stat == "vaultspace":
        sort_by_ascending = True

        leaderboard_text = "Top Clanmembers by D2 Vaultspace Used"
        stat_text = "Used Space"

        result_sort = len(await getInventoryBucket(destinyID))
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

    elif stat == "forges":
        leaderboard_text = "Top Clanmembers by D2 Forge Completions"
        stat_text = "Total"

        result_sort = 0
        farmed_runs = 0
        async for activity in getPlayersPastActivities(destinyID, mode=66):
            # set this run as a farmed run if you haven't killed anything
            if activity["values"]["opponentsDefeated"]["basic"]["value"] == 0:
                farmed_runs += 1
            else:
                result_sort += 1

        result = f"{result_sort:,} + {farmed_runs:,} AFK runs"

    elif stat == "afkforges":
        leaderboard_text = "Top Clanmembers by D2 AFK Forge Completions"
        stat_text = "Total"

        runs = 0
        result_sort = 0
        async for activity in getPlayersPastActivities(destinyID, mode=66):
            # set this run as a farmed run if you haven't killed anything
            if activity["values"]["opponentsDefeated"]["basic"]["value"] == 0:
                result_sort += 1
            else:
                runs += 1

        result = f"{runs:,} + {result_sort:,} AFK runs"

    elif stat == "enhancementcores":
        leaderboard_text = "Top Clanmembers by D2 Total Enhancement Cores"
        stat_text = "Total"

        result_sort = 0

        # check vault
        items = await getInventoryBucket(destinyID)
        for item in items:
            if item["itemHash"] == 3853748946:
                result_sort += item["quantity"]

        items = await getInventoryBucket(destinyID, bucket=1469714392)
        for item in items:
            if item["itemHash"] == 3853748946:
                result_sort += item["quantity"]
        result = f"{result_sort:,}"

    elif stat == "weapon":
        leaderboard_text = f"Top Clanmembers by {extra_name} Kills"
        stat_text = "Kills"

        result_sort, _ = await getWeaponStats(destinyID, extra_hash)
        result = f"{result_sort:,}"

    elif stat == "weaponprecision":
        leaderboard_text = f"Top Clanmembers by {extra_name} Precision Kills"
        stat_text = "Kills"

        _, result_sort = await getWeaponStats(destinyID, extra_hash)
        result = f"{result_sort:,}"

    elif stat == "weaponprecisionpercent":
        leaderboard_text = f"Top Clanmembers by {extra_name} % Precision Kills"
        stat_text = "Kills"

        kills, prec_kills = await getWeaponStats(destinyID, extra_hash)
        result_sort = prec_kills / kills if kills != 0 else 0
        result = f"{round(result_sort*100, 2)}%"

    elif stat == "armor":
        leaderboard_text = f"Top Clanmembers by single Armor Piece with highest {extra_name.capitalize()}"
        stat_text = "Value"

        items = await getAllGear(destinyID)
        system = lookupSystem(destinyID)

        # clean items so that only entries with instanceID remain
        items_clean = []
        for item in items:
            if "itemInstanceId" in item:
                items_clean.append(item)

        results = await asyncio.gather(*[get_armor_stat(destinyID, system, item["itemInstanceId"], extra_hash) for item in items_clean])

        result_sort = 0
        for ret in results:
            if ret and (ret > result_sort):
                result_sort = ret
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


async def get_armor_stat(destinyID, system, itemInstanceId, extra_hash):
    try:
        return (await getItemDefinition(destinyID, system, itemInstanceId, 304))["stats"]["data"]["stats"][str(extra_hash)]["value"]
    except KeyError:
        return None

# takes list of items and sorts them
def sort_gear_by_slot(items):
    helmet = []         # 3448274439
    gauntlet = []       # 3551918588
    chest = []          # 14239492
    leg = []            # 20886954
    class_item = []     # 1585787867

    kinetic = []        # 1498876634
    energy = []         # 2465295065
    power = []          # 953998645

    for item in items:
        if item["bucketHash"] == 3448274439:
            helmet.append(item)
        elif item["bucketHash"] == 3551918588:
            gauntlet.append(item)
        elif item["bucketHash"] == 14239492:
            chest.append(item)
        elif item["bucketHash"] == 20886954:
            leg.append(item)
        elif item["bucketHash"] == 1585787867:
            class_item.append(item)

        elif item["bucketHash"] == 1498876634:
            kinetic.append(item)
        elif item["bucketHash"] == 2465295065:
            energy.append(item)
        elif item["bucketHash"] == 953998645:
            power.append(item)

    return [helmet, gauntlet, chest, leg, class_item, kinetic, energy, power]


async def get_highest_item_light_level(destinyID, system, items):
    #TODO not overload network
    max_power = 0

    for item in items:
        if item['lightlevel'] > max_power:
            max_power = item['lightlevel']
    return max_power
