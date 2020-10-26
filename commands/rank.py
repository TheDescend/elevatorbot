from commands.base_command  import BaseCommand
from functions.dataLoading import getStats
from functions.database import lookupDiscordID
from functions.formating import embed_message
from functions.network import getJSONfromURL
from static.config import CLANID

import pandas
import asyncio
import random


class rank(BaseCommand):
    # shadows charleys rank command. Currently works with "totaltime", "maxpower"
    def __init__(self):
        # A quick description for the help message
        description = "Shadows various Charley leaderboards with only clan members shown"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        supported = [
            "totaltime",
            "maxpower"
        ]

        if len(params) == 1 and params[0] in supported:
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
        data = data.append({"member": ret[0], "stat": ret[1], "stat_sort": ret[2]}, ignore_index=True)

    # the flavor text of the leaderboard, fe "Top Clanmembers by D2 Total Time Logged In" for totaltime
    leaderboard_text = results[0][3]
    # the flavor text the stat will have, fe. "hours" for totaltime
    stat_text = results[0][4]
    # for some stats lower might be better
    sort_by_ascending = results[0][5]

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
        name = random.randint(1, 100000)
        # continue

    # get the stat that we are looking for
    if stat == "totaltime":
        leaderboard_text = "Top Clanmembers by D2 Total Time Logged In"
        stat_text = "Hours"

        # in hours
        json = await getStats(destinyID)
        result_sort = int(json["mergedAllCharacters"]["merged"]["allTime"]["secondsPlayed"]["basic"]["value"] / 60 / 60)
        try:
            result_sort += int(json["mergedDeletedCharacters"]["merged"]["allTime"]["secondsPlayed"]["basic"]["value"] / 60 / 60)
        except:
            pass
        result = f"{result_sort:,}"

    elif stat == "maxpower":
        leaderboard_text = "Top Clanmembers by D2 Maximum Reported Power"
        stat_text = "Power"

        json = await getStats(destinyID)
        result_sort = int(json["mergedAllCharacters"]["merged"]["allTime"]["highestLightLevel"]["basic"]["value"])
        result = f"{result_sort:,}"

    else:
        return

    return [name, result, result_sort, leaderboard_text, stat_text, sort_by_ascending]

def write_line(index, member, stat_text, stat):
    return f"{index}) **{member}** _({stat_text}: {stat})_"


