from static.config          import BUNGIE_TOKEN
from commands.base_command  import BaseCommand
from functions.database     import lookupDestinyID, getAllDiscordMemberDestinyIDs
from functions.network  import getJSONfromURL

import numpy as np
import datetime
import discord
import time
import os
import concurrent.futures

from collections import Counter
from pyvis.network import Network

# note: the ids later are formatted so wierd, because pyvis broke with them being 16 numbers or so. So I'm just shorting them in an ugly way that works


# !friends <activity> <time-period> *<user>
class friends(BaseCommand):
    def __init__(self):
        description = f'Shows information about who you play with. For options, type "!friends"'
        params = []
        super().__init__(description, params)

        self.ignore = []


    async def handle(self, params, message, client):
        PARAMS = {'X-API-Key': BUNGIE_TOKEN}

        activities = {
            "pve": 7,
            "pvp": 5,
            "raids": 4,
            "strikes": 3
        }
        time_periods = ["week", "month", "6months", "year", "all-time"]

        # check if message too short / long
        if len(params) < 2 or len(params) > 3:
            await message.channel.send(embed=self.embed_message('Error', 'Incorrect formatting, correct usage is: "!friends <activity> <time-period> *<user>"'))
            return

        # check if activity is correct
        if params[0] not in activities:
            await message.channel.send(embed=self.embed_message('Error', 'Unrecognised activity, currently supported are: "pve", "pvp", "raids", "strikes"'))
            return
        activityID = activities[params[0]]

            # check if time period is correct
        if params[1] not in time_periods:
            await message.channel.send(embed=self.embed_message('Error', 'Unrecognised time period, currently supported are: "week", "month", "6months", "year". "all-time"'))
            return

        # set user to the one that send the message, or if a third param was used, the one mentioned
        if len(params) == 3:
            ctx = await client.get_context(message)
            try:
                user = await discord.ext.commands.MemberConverter().convert(ctx, params[2])
            except:
                await message.channel.send(embed=self.embed_message('Error', 'User not found, make sure the spelling/id is correct'))
                return
        else:
            user = message.author

        # letting the user know that this might take a while
        status = await message.channel.send(embed=self.embed_message(f'Please Wait {user.name}', f"This might take a while, I'll ping you when I'm done.", f"Collecting data - 0% done!"))
        status_msg = await message.channel.fetch_message(status.id)


        # >> Do the actual work <<
        destinyID = int(lookupDestinyID(user.id))
        unique_users = []
        activities_from_user_who_got_looked_at = {}

        # gets all discord member destiny ids
        discordMemberIDs = getAllDiscordMemberDestinyIDs()
        # changing them to be in a simple list instead of tuple inside of a list
        for i in range(len(discordMemberIDs)):
            discordMemberIDs[i] = int(discordMemberIDs[i][0])

        # getting the activities for the original user
        result = self.return_activities(destinyID, activityID, params[1])
        activities_from_user_who_got_looked_at[destinyID] = len(result[1])

        # getting the friends from his activities
        friends = []
        for ID in result[1]:
            result = self.return_friends(destinyID, ID)
            friends.extend(result)
        friends = dict(Counter(friends))

        # to avoid double dipping
        self.ignore.append(destinyID)

        # no need to continue of list is empty
        if not friends:
            await status_msg.delete()
            await message.channel.send(embed=self.embed_message('Sorry', f'You have to play any {params[0]} before I can show you something here <:PepeLaugh:670369129060106250>'))
            return

        # initialising the big numpy array with all the data
        data_temp = []
        for friend in friends:
            if int(friend) != destinyID:
                # data = [user1, user2, number of activities together]
                data_temp.append([int(str(destinyID)[-9:]), int(str(friend)[-9:]), friends[friend]])

                if int(friend) not in discordMemberIDs:
                    unique_users.append(int(friend))
        data = np.array(data_temp)

        # math on how long this is approximately going to take. Starts with 1 to factor in the user himself
        estimated_current = 1
        estimated_total = 1
        for friend in friends:
            if int(friend) in discordMemberIDs:
                estimated_total +=1
        # updating the user how far along we are
        progress = int(estimated_current / estimated_total * 100)
        await status_msg.edit(embed=self.embed_message(f'Please Wait {user.name}', f"This might take a while, I'll ping you when I'm done.",f"Collecting data - {progress}% done!"))

        # looping through friends and doing the same IF they are in the discord and new
        friends_cleaned = []
        for friend in friends:
            friend = int(friend)
            if (friend not in self.ignore) and (friend in discordMemberIDs):
                friends_cleaned.append(friend)

        # getting the activities each user did
        list_of_activities = []
        with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 5) as pool:
            futurelist = [pool.submit(self.return_activities, friend, activityID, params[1]) for friend in friends_cleaned]
            for future in concurrent.futures.as_completed(futurelist):
                try:
                    result = future.result()
                    if result:
                        list_of_activities.append(result)

                        # adding their # of activites to the dict
                        activities_from_user_who_got_looked_at[int(result[0])] = len(result[1])

                except Exception as exc:
                    print(f'generated an exception: {exc}')

        print("Finished getting the activityIDs")

        # looping through users and their activities
        for activities in list_of_activities:
            friend = activities[0]
            friends_friends = []

            # looping through activities to get the data
            with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 5) as pool:
                futurelist = [pool.submit(self.return_friends, friend, ID) for ID in activities[1]]
                for future in concurrent.futures.as_completed(futurelist):
                    try:
                        result = future.result()
                        if result:
                            friends_friends.extend(result)

                    except Exception as exc:
                        print(f'generated an exception: {exc}')

            data_temp = []
            friends_friends = dict(Counter(friends_friends))

            # adding their data to the numpy array
            for friends_friend in friends_friends:
                if int(friends_friend) != int(friend):
                    data_temp.append([int(str(friend)[-9:]), int(str(friends_friend)[-9:]), friends_friends[friends_friend]])
                    # adding the user to a list, if he wasn't looked at in the 2nd run
                    if int(friends_friend) not in friends_cleaned:
                        unique_users.append(int(friends_friend))
            try:
                data = np.append(data, data_temp, axis=0)
            except Exception as exc:
                print(f'Error adding to dataset: {data_temp}')
                print(f'generated an exception: {exc}')

            # to avoid double dipping
            self.ignore.append(friend)

            # updating the status
            progress = int(estimated_current / estimated_total * 100)
            await status_msg.edit(embed=self.embed_message(f'Please Wait {user.name}', f"This might take a while, I'll ping you when I'm done.",f"Collecting data - {progress}% done!"))
            estimated_current += 1

        print("Finished getting the activity infos")

        # some last data prep
        await status_msg.edit(embed=self.embed_message(f'Please Wait {user.name}', f"This might take a while, I'll ping you when I'm done.",f"Preparing data - 0% done!"))

        # removing users with less than 2 occurences from the dataset, to remove clutter
        count_users = dict(Counter(unique_users))
        unique_users = []
        for name in count_users:
            if name != destinyID:
                if count_users[name] < 2:
                    continue
            unique_users.append(int(name))

        # adding the user that are in the discord to the unique users list
        for name in activities_from_user_who_got_looked_at:
            unique_users.append(int(name))

        unique_users = set(unique_users)
        display_names = []
        colors = []
        size = []
        size_desc = []

        # calculating stuff for the status message
        estimated_current = 1
        estimated_total = len(unique_users) + 1

        # getting the display names, colors for users in discord, size of blob
        for person in unique_users:
            name = self.get_display_name(person)
            display_names.append(name)
            if person not in friends_cleaned and person != destinyID:
                size.append(count_users[person] * 50)
                size_desc.append(str(count_users[person]) + " Activities")
            else:
                size.append(activities_from_user_who_got_looked_at[person] * 50)
                size_desc.append(str(activities_from_user_who_got_looked_at[person]) + " Activities")
            # using different colors for users in discord
            if person != destinyID:
                if person in discordMemberIDs:
                    colors.append("#00ff1e")
                else:
                    colors.append("#162347")
            # using a different color for initiator
            else:
                colors.append("#dd4b39")

            # updating the status
            progress = int(estimated_current / estimated_total * 100)
            await status_msg.edit(embed=self.embed_message(f'Please Wait {user.name}',f"This might take a while, I'll ping you when I'm done.",f"Preparing data - {progress}% done!"))
            estimated_current += 1

        # print(unique_users)
        # print(count_users)
        # print(activities_from_user_who_got_looked_at)
        # print(display_names)
        # print(colors)
        # print(size)
        # print(data)
        # print(data.shape)

        # building the network graph
        await status_msg.edit(embed=self.embed_message(f'Please Wait {user.name}', f"This might take a while, I'll ping you when I'm done.",f"Building the graph, nearly done!"))
        net = Network()

        # adding nodes
        for ID, value, title, label, color in zip(unique_users, size, size_desc, display_names, colors):
            net.add_node(int(str(ID)[-9:]), value=value, title=title, label=label, color=color)

        # adding edges with data = [user1, user2, number of activities together]
        with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 5) as pool:
            futurelist = [pool.submit(self.add_edge, net, edge, unique_users) for edge in data]
            for future in concurrent.futures.as_completed(futurelist):
                pass

        net.barnes_hut(gravity=-200000, central_gravity=0.3, spring_length=200, spring_strength=0.005, damping=0.09, overlap=0)
        net.show_buttons(filter_=["physics"])

        # saving the file
        title = user.name + ".html"
        net.save_graph(title)

        # deleting the status
        await status_msg.delete()
        # letting user know it's done
        await message.channel.send(embed=self.embed_message('Done!', "Use the Link below to download your Network.", f"The file may load for a long time, that's normal."))
        # sending them the file
        await message.channel.send(file=discord.File(title))
        # pinging the user
        await message.channel.send(user.mention)

        # delete file
        os.remove(title)

    # returns embeded message
    def embed_message(self, title, desc, footer=None):
        embed = discord.Embed(
            title=title,
            description=desc
        )
        if footer:
            embed.set_footer(text=footer)
        return embed

    def get_display_name(self, destinyID, loop=0):
        staturl = f"https://www.bungie.net/Platform/Destiny2/3/Profile/{destinyID}/?components=100"
        rep = getJSONfromURL(staturl)

        if rep and rep['Response']:
            return rep["Response"]["profile"]["data"]["userInfo"]["displayName"]
        # try psn / xbox, if that fails - return error if looped 5 times
        elif loop == 5:
            # xbox
            staturl = f"https://www.bungie.net/Platform/Destiny2/1/Profile/{destinyID}/?components=100"
            rep = getJSONfromURL(staturl)

            if rep and rep['Response']:
                return rep["Response"]["profile"]["data"]["userInfo"]["displayName"]
            else:
                # psn
                staturl = f"https://www.bungie.net/Platform/Destiny2/2/Profile/{destinyID}/?components=100"
                rep = getJSONfromURL(staturl)

                if rep and rep['Response']:
                    return rep["Response"]["profile"]["data"]["userInfo"]["displayName"]
                else:
                    print(f"Error getting name {destinyID}")
                    return destinyID
        else:
            # doing that until I get the name, added a delay to relax bungie
            loop += 1
            time.sleep(1)
            return self.get_display_name(destinyID, loop)

    def return_activities(self, destinyID, activityID, time_period):
        # waiting a bit so we don't get throttled by bungie
        time.sleep(0.3)

        # stoping this if user is in ignore
        if destinyID in self.ignore:
            return None

        now = datetime.datetime.now()
        cutoff = datetime.datetime.strptime("1900", "%Y")
        if time_period == "week":
            cutoff = now - datetime.timedelta(weeks=1)
        elif time_period == "month":
            cutoff = now - datetime.timedelta(weeks=4)
        elif time_period == "6months":
            cutoff = now - datetime.timedelta(weeks=26)
        elif time_period == "year":
            cutoff = now - datetime.timedelta(weeks=52)

        destinyID = int(destinyID)

        # get get character ids
        staturl = f"https://www.bungie.net/Platform/Destiny2/3/Profile/{destinyID}/?components=100"
        rep = getJSONfromURL(staturl)
        activities = []

        if rep and rep['Response']:
            # loop for all 3 chars
            for characterID in rep["Response"]["profile"]["data"]["characterIds"]:
                br = False
                for page in range(1000):
                    # break loop if time period is met
                    if br:
                        break

                    staturl = f"https://www.bungie.net/Platform/Destiny2/3/Account/{destinyID}/Character/{characterID}/Stats/Activities/?mode={activityID}&count=250&page={page}"
                    rep = getJSONfromURL(staturl)

                    if rep and rep['Response']:
                        for activity in rep["Response"]["activities"]:

                            # check that activity is completed
                            if activity["values"]["completionReason"]["basic"]["displayValue"] == "Objective Completed":

                                # check if time-period is not OK, else break the loop
                                if datetime.datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ") < cutoff:
                                    br = True
                                else:
                                    # add instanceID to activities list
                                    activities.append(activity["activityDetails"]["instanceId"])
                    else:
                        break

        return [destinyID, set(activities)]

    def return_friends(self, destinyID, instanceID):
        # waiting a bit so we don't get throttled by bungie
        time.sleep(0.3)

        # list in which the connections are saved
        friends = []

        # get instance id info
        staturl = f"https://stats.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{instanceID}"
        rep = getJSONfromURL(staturl)

        if rep and rep['Response']:
            for player in rep["Response"]["entries"]:
                friendID = int(player["player"]["destinyUserInfo"]["membershipId"])

                # for all friends not in ignore
                if friendID not in self.ignore:
                    # doesn't make sense to add yourself
                    if friendID != destinyID:
                        friends.append(friendID)

        # sort and count friends
        return friends

    def add_edge(self, network, edge, IDs):
        src = int(edge[0])
        dst = int(edge[1])
        value = int(edge[2])

        # only add edge if non of both users got removed because < activity
        if int("4611686018" + str(src)) in IDs and int("4611686018" + str(dst)) in IDs:
            try:
                network.add_edge(src, dst, value=value, title=value, physics=True)
            except:
                print("error adding node")
            try:
                network.add_edge(dst, src, value=value, title=value, physics=True)
            except:
                print("error adding node")