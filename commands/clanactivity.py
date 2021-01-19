import asyncio
import concurrent.futures
import datetime
import os
from collections import Counter

import discord
import numpy as np
from pyvis.network import Network

from commands.base_command import BaseCommand
from functions.dataLoading import getClanMembers, getProfile, getPlayersPastActivities
from functions.database import lookupDestinyID
from functions.formating import embed_message
from functions.network import getJSONfromURL


# note: the ids later are formatted so wierd, because pyvis broke with them being 16 numbers or so. So I'm just shorting them in an ugly way that works


# !friends <activity> <time-period> *<user>
class clanActivity(BaseCommand):
    def __init__(self):
        description = f'Shows information about who you play with. For options, type "!friends"'
        topic = "Destiny"
        params = []
        super().__init__(description, params, topic)

        self.ignore = []
        # edge_list = [person, size, size_desc, display_names, colors]
        self.edge_list = []

    async def handle(self, params, message, mentioned_user, client):
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
        if len(params) == 0:
            await message.channel.send(embed=embed_message(
                'Error',
                 'Incorrect formatting, correct usage is: \n\u200B\n `!clanActivity <activity>`'
            ))
            return

        # check if activity is correct. Also allow the int number for more activities
        if params[0] not in activities:
            try:
                params[0] = int(params[0])
            except ValueError:
                await message.channel.send(embed=embed_message(
                    'Error',
                    f'Unrecognised activity, currently supported are: \n\u200B\n`{", ".join(activities)}` \n\u200B\nand all of Bungies component numbers if you know them`'
                ))
                return
        mode = activities[params[0]] if (type(params[0]) != int) else params[0]

        # asking user to give time-frame
        time_msg = await message.channel.send(embed=embed_message(
            f'{message.author.name}, I need one more thing',
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
                f'Sorry {message.author.name}',
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
            f'Please Wait {message.author.name}',
            f"This might take a while, I'll ping you when I'm done.",
            f"Collecting data - 0% done!"
        ))
        status_msg = await message.channel.fetch_message(status_msg.id)

        # >> Do the actual work <<

        # get clanmembers
        self.clan_members = await getClanMembers(client)
        self.activities_from_user_who_got_looked_at = {}
        self.friends = {}

        # math on how long this is approximately going to take. Starts with 1 to factor in the user himself
        self.estimated_current = 1
        self.estimated_total = 1
        for _ in self.clan_members:
            self.estimated_total += 1

        result = await asyncio.gather(*[self.handle_members(destinyID, mode, start_time, end_time, status_msg, mentioned_user.name) for destinyID in self.clan_members])
        for res in result:
            if res is not None:
                destinyID = res[0]

                self.activities_from_user_who_got_looked_at[destinyID] = res[1]
                self.friends[destinyID] = res[2]

        # loop through all clan members

        # filling the big numpy array with all the data
        data_temp = []
        for destinyID in self.friends:
            for friend in self.friends[destinyID]:
                # data = [destinyID1, destinyID2, number of activities together]
                data_temp.append([int(str(destinyID)[-9:]), int(str(friend)[-9:]), self.friends[destinyID][friend]])

        data = np.array(data_temp)
        del data_temp

        # some last data prep
        await status_msg.edit(embed=embed_message(
            f'Please Wait {message.author.name}',
            f"This might take a while, I'll ping you when I'm done.",
            f"Preparing data - 0% done!"
        ))

        # calculating stuff for the status message
        self.estimated_current = 1
        self.estimated_total = len(self.clan_members) + 1

        # getting the display names, colors for users in discord, size of blob
        orginal_user_destiny_id = lookupDestinyID(mentioned_user.id)
        await asyncio.gather(*[self.prep_data(status_msg, mentioned_user.name, destinyID, orginal_user_destiny_id) for destinyID in self.clan_members])

        # building the network graph
        await status_msg.edit(embed=embed_message(
            f'Please Wait {message.author.name}',
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
            futurelist = [pool.submit(self.add_edge, net, edge) for edge in data]
            for _ in concurrent.futures.as_completed(futurelist):
                pass

        net.barnes_hut(gravity=-200000, central_gravity=0.3, spring_length=200, spring_strength=0.005, damping=0.09, overlap=0)
        net.show_buttons(filter_=["physics"])

        # saving the file
        title = mentioned_user.name + ".html"
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
        await message.channel.send(mentioned_user.mention)

        # delete file
        os.remove(title)

    async def handle_members(self, destinyID, mode, start_time, end_time, status_msg, name):
        # getting the activities for the
        result = await self.return_activities(destinyID, mode, start_time, end_time)
        activities_from_user_who_got_looked_at = len(result[1])

        # getting the friends from his activities
        destinyIDs_friends = []
        for ID in result[1]:
            result = await self.return_friends(destinyID, ID)
            destinyIDs_friends.extend(result)
        friends = dict(Counter(destinyIDs_friends))

        # updating the user how far along we are
        self.estimated_current += 1
        progress = int(self.estimated_current / self.estimated_total * 100)
        await status_msg.edit(embed=embed_message(
            f'Please Wait {name}'
            , f"This might take a while, I'll ping you when I'm done.",
            f"Collecting data - {progress}% done!"
        ))

        return [destinyID, activities_from_user_who_got_looked_at, friends]


    async def get_display_name(self, destinyID):
        return (await getProfile(destinyID, 100))["profile"]["data"]["userInfo"]["displayName"]

    async def return_activities(self, destinyID, mode, start_time, end_time):
        destinyID = int(destinyID)
        activities = []

        # loop through activities
        async for activity in getPlayersPastActivities(destinyID, mode=mode, earliest_allowed_time=start_time, latest_allowed_time=end_time):
            # check that activity is completed
            if activity["values"]["completionReason"]["basic"]["displayValue"] == "Objective Completed":
                activities.append(activity["activityDetails"]["instanceId"])

        return [destinyID, set(activities)]

    async def return_friends(self, destinyID, instanceID):
        # waiting a bit so we don't get throttled by bungie
        await asyncio.sleep(0.3)

        # list in which the connections are saved
        friends = []

        # get instance id info
        staturl = f"https://stats.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{instanceID}"
        rep = await getJSONfromURL(staturl)

        if rep and rep['Response']:
            for player in rep["Response"]["entries"]:
                friendID = int(player["player"]["destinyUserInfo"]["membershipId"])

                # only look at clan members
                if friendID in self.clan_members:
                    # doesn't make sense to add yourself
                    if friendID != destinyID:
                        friends.append(friendID)

        # sort and count friends
        return friends

    async def prep_data(self, status_msg, name, destinyID, orginal_user_destiny_id):
        display_name = await self.get_display_name(destinyID)

        size = self.activities_from_user_who_got_looked_at[destinyID] * 50
        size_desc = str(self.activities_from_user_who_got_looked_at[destinyID]) + " Activities"

        colors = "#850404" if orginal_user_destiny_id == destinyID else "#006aff"

        # edge_list = [person, size, size_desc, display_names, colors]
        self.edge_list.append([destinyID, size, size_desc, display_name, colors])

        # updating the status
        progress = int(self.estimated_current / self.estimated_total * 100)
        await status_msg.edit(embed=embed_message(
            f'Please Wait {name}',
            f"This might take a while, I'll ping you when I'm done.",
            f"Preparing data - {progress}% done!"
        ))
        self.estimated_current += 1

    def add_edge(self, network, edge):
        src = int(edge[0])
        dst = int(edge[1])
        value = int(edge[2])

        # add the edge
        try:
            network.add_edge(dst, src, value=value, title=value, physics=True)
        except:
            print("error adding node")
