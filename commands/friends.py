from static.config          import BUNGIE_TOKEN
from commands.base_command  import BaseCommand
from functions.database     import lookupDestinyID, getAllDiscordMemberDestinyIDs
from functions.network  import getJSONfromURL

import numpy as np
import datetime
import discord
from pyvis.network import Network
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
        if len(params) == 3:
            ctx = await client.get_context(message)
            try:
                user = await discord.commands.MemberConverter().convert(ctx, params[2])
            except:
                await message.channel.send(embed=embed_message('Error', 'User not found, make sure the spelling/id is correct'))
                return
        else:
            user = message.author

        # letting the user know that this might take a while
        status = await message.channel.send(embed=embed_message(f'Please Wait {user.name}', f"This might take a while, I'll ping you when I'm done.", f"Collecting data - 0% done!"))
        status_msg = await message.channel.fetch_message(status.id)

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
        unique_users = [destinyID]
        friends = return_friends(ignore, destinyID, activityID, params[1])

        # to avoid double dipping
        ignore.append(int(destinyID))
        unique_users.append(int(destinyID))

        # no need to continue of list is empty
        if not friends:
            await status_msg.delete()
            await message.channel.send(embed=embed_message('Sorry', f'You have to play any {params[0]} before I can show you something here <:PepeLaugh:670369129060106250>'))
            return

        # initialising the big numpy array with all the data
        data_temp = []
        for friend in friends:
            friend = friend
            # data = [user1, user2, number of activities together]
            data_temp.append([destinyID, friend, friends[friend]])
            unique_users.append(int(friend))
        data = np.array(data_temp)

        # gets all discord member destiny ids
        discordMemberIDs = getAllDiscordMemberDestinyIDs()
        # changing them to be in a simple list instead of tuple inside of a list
        for i in range(len(discordMemberIDs)):
            discordMemberIDs[i] = int(discordMemberIDs[i][0])

        # math on how long this is approximately going to take. Starts with 1 to factor in the user himself
        estimated_current = 1
        estimated_total = 1
        for friend in friends:
            if int(friend) in discordMemberIDs:
                estimated_total +=1
        # updating the user how far along we are
        progress = int(estimated_current / estimated_total * 100)
        await status_msg.edit(embed=embed_message(f'Please Wait {user.name}', f"This might take a while, I'll ping you when I'm done.",f"Collecting data - {progress}% done!"))


        # looping through friends and doing the same IF they are in the discord and new
        for friend in friends:
            friend = int(friend)
            if (friend not in ignore) and (friend in discordMemberIDs):
                friends_friends = return_friends(ignore, friend, activityID, params[1])

                # adding them to ignore
                ignore.append(friend)

                # adding their data to the numpy array
                data_temp = []
                for friends_friend in friends_friends:
                    data_temp.append([friend, friends_friend, friends_friends[friends_friend]])
                    unique_users.append(friends_friend)
                try:
                    data = np.append(data, data_temp, axis=0)
                except:
                    pass

                # updateing the status
                estimated_current += 1
                progress = int(estimated_current / estimated_total * 100)
                await status_msg.edit(embed=embed_message(f'Please Wait {user.name}', f"This might take a while, I'll ping you when I'm done.", f"Collecting data - {progress}% done!"))

                print(data.shape)
        print(data.shape)

        # some last data prep
        await status_msg.edit(embed=embed_message(f'Please Wait {user.name}', f"This might take a while, I'll ping you when I'm done.",f"Preparing data - 0% done!"))

        # getting the display names, colors for users in discord, size of blob
        count_users = dict(Counter(unique_users))
        unique_users = set(unique_users)
        display_names = []
        colors = []
        size = []
        for person in unique_users:
            name = get_display_name(person)
            display_names.append(name)
            if person in discordMemberIDs:
                colors.append("#00ff1e")
            else:
                colors.append("#162347")
            size.append(count_users[person])

            # updating the status
            progress = int(estimated_current / estimated_total * 100)
            await status_msg.edit(embed=embed_message(f'Please Wait {user.name}',f"This might take a while, I'll ping you when I'm done.",f"Preparing data - {progress}% done!"))

        print(data)
        print(unique_users)
        print(display_names)
        print(colors)
        print(size)


        # building the network graph
        await status_msg.edit(embed=embed_message(f'Please Wait {user.name}', f"This might take a while, I'll ping you when I'm done.",f"Building the graph, nearly done!"))
        net = Network()

        # adding nodes
        net.add_nodes(list(unique_users), label=display_names, value=size, title=display_names)

        # adding edges with data = [user1, user2, number of activities together]
        for edge in data:
            src = int(edge[0])
            dst = int(edge[1])
            value = int(edge[2])

            try:
                net.add_edge(src, dst, value=value, title=value, physics=True)
            except:
                print("error adding node")
            try:
                net.add_edge(dst, src, value=value, title=value, physics=True)
            except:
                print("error adding node")


        net.toggle_physics(True)
        title = user.name + ".html"
        net.show(title)





        # deleting the status
        await status_msg.delete()
        # letting user know it's done
        await message.channel.send(embed=embed_message('Done!', 'some text'))
        await message.channel.send(user.mention)

        # delete file


# returns embeded message
def embed_message(title, desc, footer=None):
    embed = discord.Embed(
        title=title,
        description=desc
    )
    if footer:
        embed.set_footer(text=footer)
    return embed

def get_display_name(destinyID):
    staturl = f"https://www.bungie.net/Platform/Destiny2/3/Profile/{destinyID}/?components=100"
    rep = getJSONfromURL(staturl)

    if rep and rep['Response']:
        return rep["Response"]["profile"]["data"]["userInfo"]["displayName"]
    else:
        # trying to get the name again
        rep = getJSONfromURL(staturl)
        if rep and rep['Response']:
            return rep["Response"]["profile"]["data"]["userInfo"]["displayName"]
        return "Error getting name"

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

    if rep and rep['Response']:
        # loop for all 3 chars
        for characterID in rep["Response"]["profile"]["data"]["characterIds"]:
            staturl = f"https://www.bungie.net/Platform/Destiny2/3/Account/{destinyID}/Character/{characterID}/Stats/Activities/?mode={activityID}"
            rep = getJSONfromURL(staturl)

            if rep and rep['Response']:
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

        if rep and rep['Response']:
            for player in rep["Response"]["entries"]:
                friendID = player["player"]["destinyUserInfo"]["membershipId"]

                # for all friends not in ignore
                if friendID not in ignore:
                    # doesn't make sense to add yourself
                    if friendID != destinyID:
                        friends.append(friendID)

    # sort and count friends
    return dict(Counter(friends))