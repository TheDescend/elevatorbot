from static.config          import BUNGIE_TOKEN
from commands.base_command  import BaseCommand
from functions.database     import lookupDestinyID
from functions.network  import getJSONfromURL

import numpy as np
import datetime
import discord
from collections import Counter


# !friends <activity> <time-period> *<user>
class friends(BaseCommand):
    def __init__(self):
        description = "Shows information about who you play with"
        params = []
        super().__init__(description, params)


    async def handle(self, params, message, client):
        PARAMS = {'X-API-Key': BUNGIE_TOKEN}
        activities = ["pve", "pvp", "raids", "strikes"]
        #               7      5       4         3
        time_periods = ["week", "month", "year", "all-time"]

        # check if message too short / long
        if len(params) < 2 or len(params) > 3:
            await message.channel.send(embed=embed_message('Error', 'Incorrect formatting, correct usage is: "!friends <activity> <time-period> *<user>"'))
            return

        # check if activity is correct
        if params[0] not in activities:
            await message.channel.send(embed=embed_message('Error', 'Unrecognised activity, currently supported are: "pve", "pvp", "raids", "strikes"'))
            return
        if params[0] == "pve":
            activityID = 7
        elif params[0] == "pvp":
            activityID = 5
        elif params[0] == "raids":
            activityID = 4
        elif params[0] == "strikes":
            activityID = 3

            # check if time period is correct
        if params[1] not in time_periods:
            await message.channel.send(embed=embed_message('Error', 'Unrecognised time period, currently supported are: "week", "month", "year". "all-time"'))
            return

        # set user to the one that send the message, or if a third param was used, the one mentioned
        username = message.author.nick or message.author.name
        if len(params) == 3:
            ctx = await client.get_context(message)
            try:
                user = await discord.commands.MemberConverter().convert(ctx, params[2])
            except:
                await message.channel.send(embed=embed_message('Error', 'User not found, make sure the spelling/id is correct'))
                return
        else:
            user = message.author

        #   >> PLAN <<
        # get activites by user
        # put all the friends in there in a list user = [friend1, friend2]
        # add user to ignore list, to avoid double dipping
        # check the set(user) if friend is in clan
        # if friend is in clan, get his activities and put his friends in a list SHOULD they already exist in the original users friends and SHOULD they not already be in the ignore list
        # add friend to ignore list and continue
        # make a new array with all the information:
            # info = [[person1, person2, # of activities], ...]

        destinyID = lookupDestinyID(user.id)
        ignore = []
        friends = return_friends(ignore, destinyID, activityID, params[1])
        print(len(friends))
        print(friends)


# returns embeded message
def embed_message(title, desc):
    embed = discord.Embed(
        title=title,
        description=desc
    )
    return embed

def return_friends(ignore, destinyID, activityID, time_period):
    now = datetime.datetime.now()
    cutoff = datetime.datetime.strptime("1900", "%Y")
    if time_period == "week":
        cutoff = now - datetime.timedelta(weeks = 1)
    elif time_period == "month":
        cutoff = now - datetime.timedelta(weeks = 4)
    elif time_period == "year":
        cutoff = now - datetime.timedelta(weeks = 52)

    # get get character ids
    staturl = f"https://www.bungie.net/Platform/Destiny2/3/Profile/{destinyID}/?components=100"
    rep = getJSONfromURL(staturl)
    activities = []

    # loop for all 3 chars
    for characterID in rep["Response"]["profile"]["data"]["characterIds"]:
        staturl = f"https://www.bungie.net/Platform/Destiny2/3/Account/{destinyID}/Character/{characterID}/Stats/Activities/?mode={activityID}"
        rep = getJSONfromURL(staturl)

        for activity in rep["Response"]["activities"]:

            # check that activity is completed
            if activity["values"]["completionReason"]["basic"]["displayValue"] == "Objective Completed":

                # check that time-period is OK
                if datetime.datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ") > cutoff:

                    # add instanceID to activities list
                    activities.append(activity["activityDetails"]["instanceId"])

    # list in which the connections are saved
    friends = []

    # loop through all activities
    activities = set(activities)
    for instanceID in activities:
        # get instance id info
        staturl = f"https://stats.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{instanceID}"
        rep = getJSONfromURL(staturl)

        for player in rep["Response"]["entries"]:
            friendID = player["player"]["destinyUserInfo"]["membershipId"]

            # for all friends not in ignore
            if friendID not in ignore:
                friends.append(friendID)

    # sort and count friends
    return dict(Counter(friends))