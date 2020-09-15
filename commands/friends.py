from static.config          import BUNGIE_TOKEN
from commands.base_command  import BaseCommand
from functions.database     import lookupDestinyID, getAllDiscordMemberDestinyIDs
from functions.network      import getJSONfromURL
from functions.formating    import embed_message

import numpy as np
import datetime
import discord
import asyncio
import time
import os
import concurrent.futures

from collections    import Counter
from pyvis.network  import Network

# note: the ids later are formatted so wierd, because pyvis broke with them being 16 numbers or so. So I'm just shorting them in an ugly way that works


# !friends <activity> <time-period> *<user>
class friends(BaseCommand):
    def __init__(self):
        description = f'Shows information about who you play with. For options, type "!friends"'
        topic = "Destiny"
        params = []
        super().__init__(description, params, topic)

        self.ignore = []
        # edge_list = [person, size, size_desc, display_names, colors]
        self.edge_list = []


    async def handle(self, params, message, client):
        # special behavior for pepe
        # if message.author.id == 367385031569702912:
        #     await message.channel.send(embed=embed_message(
        #         'Error',
        #         f'Pepe, we all know you have no friends. Using this command wont help you with that, now please stop sending me loli hentai <a:monkaBan:675775957906227230>'
        #     ))
        #     return

        activities = {
            "everything": 0,
            "patrol": 6,
            "pve": 7,
            "pvp": 5,
            "raids": 4,
            "story": 2,
            "strikes": 3
        }

        # check if message too short / long
        if len(params) == 0 or len(params) > 2:
            await message.channel.send(embed=embed_message(
                'Error',
                 'Incorrect formatting, correct usage is: \n\u200B\n `!friends <activity> *<user>`'
            ))
            return

        # check if activity is correct
        if params[0] not in activities:
            await message.channel.send(embed=embed_message(
                'Error',
                f'Unrecognised activity, currently supported are: \n\u200B\n`{", ".join(activities)}`'
            ))
            return
        activityID = activities[params[0]]

        # set user to the one that send the message, or if a third param was used, the one mentioned
        if len(params) == 2:
            ctx = await client.get_context(message)
            try:
                user = await discord.ext.commands.MemberConverter().convert(ctx, params[1])
            except:
                await message.channel.send(
                    embed=embed_message(
                        'Error',
                        'User not found, make sure the spelling/id is correct'
                    ))
                return
        else:
            user = message.author

        # asking user to give time-frame
        time_msg = await message.channel.send(embed=embed_message(
            f'{user.name}, I need one more thing',
            "Please specify the time-range you want the data for like this:\n\u200B\n\u200B\n \u2000 **Start** \u2005\u2001- \u2001 **End**\n `dd/mm/yy - dd/mm/yy` \n\u200B\n *If the end-time is now, you can exchange it with* `now`"
        ))
        time_msg = await message.channel.fetch_message(time_msg.id)

        # to check whether or not the one that send the msg is the original author for the function after this
        def check(answer_msg):
            return answer_msg.author == message.author and answer_msg.channel == message.channel

        # wait for reply from original user to set the time parameters
        try:
            answer_msg = await client.wait_for('message', timeout=60.0, check=check)
            try:
                await answer_msg.delete()
            except discord.errors.Forbidden:
                print(f'doesnt have admin rights for {message.channel.guild.name}')

        # if user is too slow, let him know and remove message after 30s
        except asyncio.TimeoutError:
            await time_msg.edit(embed=embed_message(
                f'Sorry {user.name}',
                f'You took to long to answer my question, type `!friends <activity> *<user>` to start over'
            ))
            await asyncio.sleep(30)
            await time_msg.delete()
            return

        # try to convert the dates to time types
        else:
            # getting the two date strings
            try:
                dates = answer_msg.content.replace(" ", "").split("-")
                start_date = dates[0]
                end_date = dates[1]
            except:
                await time_msg.edit(embed=embed_message(
                    f'Incorrect Formatting',
                    f'That was the wrong formatting, type `!friends <activity> *<user>` to start over'
                ))
                await asyncio.sleep(30)
                await time_msg.delete()
                return

            # converting the date into datetime
            try:
                start_time = datetime.datetime.strptime(start_date, "%d/%m/%y")
                if end_date == "now":
                    end_time = datetime.datetime.now()
                else:
                    end_time = datetime.datetime.strptime(end_date, "%d/%m/%y")
            except:
                await time_msg.edit(embed=embed_message(
                    f'Incorrect Formatting',
                    f'That was the wrong formatting, type `!friends <activity> *<user>` to start over'
                ))
                await asyncio.sleep(30)
                await time_msg.delete()
                return

            # throw error if end > start
            if end_time < start_time:
                await time_msg.edit(embed=embed_message(
                    f'Incorrect Formatting',
                    f'Silly you, the start-time can not be greater than the end-time. Type `!friends <activity> *<user>` to start over'
                ))
                await asyncio.sleep(30)
                await time_msg.delete()
                return
        await time_msg.delete()

        # letting the user know that this might take a while
        status_msg = await message.channel.send(embed=embed_message(
            f'Please Wait {user.name}',
            f"This might take a while, I'll ping you when I'm done.",
            f"Collecting data - 0% done!"
        ))
        status_msg = await message.channel.fetch_message(status_msg.id)


        # >> Do the actual work <<
        destinyID = int(lookupDestinyID(user.id))
        unique_users = []
        activities_from_user_who_got_looked_at = {}

        # gets all discord member destiny ids
        discordMemberIDs = getAllDiscordMemberDestinyIDs()
        # changing them to be in a simple list instead of tuple inside of a list
        for i in range(len(discordMemberIDs)):
            discordMemberIDs[i] = int(discordMemberIDs[i])

        # getting the activities for the original user
        result = self.return_activities(destinyID, activityID, start_time, end_time)
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
            await message.channel.send(embed=embed_message(
                'Sorry',
                f'You have to play any {params[0]} before I can show you something here <:PepeLaugh:670369129060106250>'
            ))
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
        await status_msg.edit(embed=embed_message(
            f'Please Wait {user.name}'
            , f"This might take a while, I'll ping you when I'm done.",
            f"Collecting data - {progress}% done!"
        ))

        # looping through friends and doing the same IF they are in the discord and new
        friends_cleaned = []
        for friend in friends:
            friend = int(friend)
            if (friend not in self.ignore) and (friend in discordMemberIDs):
                friends_cleaned.append(friend)

        # getting the activities each user did
        list_of_activities = []
        with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 5) as pool:
            futurelist = [pool.submit(self.return_activities, friend, activityID, start_time, end_time) for friend in friends_cleaned]
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
            await status_msg.edit(embed=embed_message(
                f'Please Wait {user.name}',
                f"This might take a while, I'll ping you when I'm done.",
                f"Collecting data - {progress}% done!"
            ))
            estimated_current += 1

        print("Finished getting the activity infos")

        # some last data prep
        await status_msg.edit(embed=embed_message(
            f'Please Wait {user.name}',
            f"This might take a while, I'll ping you when I'm done.",
            f"Preparing data - 0% done!"
        ))

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

        # calculating stuff for the status message
        estimated_current = 1
        estimated_total = len(unique_users) + 1

        # getting the display names, colors for users in discord, size of blob
        with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 5) as pool:
            futurelist = [pool.submit(self.prep_data, person, friends_cleaned, destinyID, discordMemberIDs, activities_from_user_who_got_looked_at, count_users) for person in unique_users]
            for _ in concurrent.futures.as_completed(futurelist):
                # updating the status
                progress = int(estimated_current / estimated_total * 100)
                await status_msg.edit(embed=embed_message(
                    f'Please Wait {user.name}',
                    f"This might take a while, I'll ping you when I'm done.",
                    f"Preparing data - {progress}% done!"
                ))
                estimated_current += 1

        # print(unique_users)
        # print(count_users)
        # print(activities_from_user_who_got_looked_at)
        # print(display_names)
        # print(data)
        # print(data.shape)
        # print(self.edge_list)

        # building the network graph
        await status_msg.edit(embed=embed_message(
            f'Please Wait {user.name}',
            f"This might take a while, I'll ping you when I'm done.",
            f"Building the graph, nearly done!"
        ))
        net = Network()

        # adding nodes
        # edge_list = [person, size, size_desc, display_names, colors]
        for edge_data in self.edge_list:
            net.add_node(int(str(edge_data[0])[-9:]), value=edge_data[1], title=edge_data[2], label=edge_data[3], color=edge_data[4])

        # adding edges with data = [user1, user2, number of activities together]
        with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 5) as pool:
            futurelist = [pool.submit(self.add_edge, net, edge, unique_users) for edge in data]
            for _ in concurrent.futures.as_completed(futurelist):
                pass

        net.barnes_hut(gravity=-200000, central_gravity=0.3, spring_length=200, spring_strength=0.005, damping=0.09, overlap=0)
        net.show_buttons(filter_=["physics"])

        # saving the file
        title = user.name + ".html"
        net.save_graph(title)

        # deleting the status
        await status_msg.delete()
        # letting user know it's done
        await message.channel.send(embed=embed_message(
            f'Done!',
            f"Use the Link below to download your Network with {params[0]} data from {answer_msg.content}.",
            f"The file may load for a while, that's normal."
        ))
        # sending them the file
        await message.channel.send(file=discord.File(title))
        # pinging the user
        await message.channel.send(user.mention)

        # delete file
        os.remove(title)

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

    def return_activities(self, destinyID, activityID, start_time, end_time):
        # waiting a bit so we don't get throttled by bungie
        time.sleep(0.3)

        # stoping this if user is in ignore
        if destinyID in self.ignore:
            return None

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
                                activity_time = datetime.datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ")
                                if activity_time < start_time:
                                    br = True
                                else:
                                    if activity_time < end_time:
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

    def prep_data(self, person, friends_cleaned, destinyID, discordMemberIDs, activities_from_user_who_got_looked_at, count_users):
        name = self.get_display_name(person)
        display_names = name
        if person not in friends_cleaned and person != destinyID:
            size = count_users[person] * 50
            size_desc = str(count_users[person]) + " Activities"
        else:
            size = activities_from_user_who_got_looked_at[person] * 50
            size_desc = str(activities_from_user_who_got_looked_at[person]) + " Activities"
        # using different colors for users in discord
        if person != destinyID:
            if person in discordMemberIDs:
                colors = "#00ff1e"
            else:
                colors = "#162347"
        # using a different color for initiator
        else:
            colors = "#dd4b39"

        # edge_list = [person, size, size_desc, display_names, colors]
        self.edge_list.append([person, size, size_desc, display_names, colors])

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