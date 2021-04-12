import json
import datetime
from collections import Counter

import discord
import asyncio
import os
import concurrent.futures
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from pyvis.network import Network

from functions.authfunctions import getSpiderMaterials
from functions.dataLoading import searchForItem, getStats, getArtifact, getCharacterGearAndPower, getInventoryBucket, \
    getProfile, getCharacterList, getAggregateStatsForChar, getPlayersPastActivities, getWeaponStats, getAllGear, \
    updateDB, getDestinyName, getTriumphsJSON, getCharacterInfoList, getCharacterID, getClanMembers
from functions.dataTransformation import getSeasonalChallengeInfo, getCharStats, getPlayerSeals, getIntStat
from functions.database import lookupDestinyID, lookupSystem, lookupDiscordID, getToken, getForges, getLastActivity, \
    getDestinyDefinition, getWeaponInfo, getPgcrActivity, getTopWeapons, getActivityHistory, getPgcrActivitiesUsersStats
from functions.formating import embed_message
from functions.miscFunctions import get_emoji, write_line, has_elevated_permissions
from functions.network import getJSONfromURL
from functions.persistentMessages import get_persistent_message, make_persistent_message, delete_persistent_message
from functions.slashCommandFunctions import get_user_obj, get_destinyID_and_system, get_user_obj_admin, \
    verify_time_input
from functions.tournament import startTournamentEvents
from static.config import GUILD_IDS, CLANID
from static.dict import metricRaidCompletion, raidHashes
from static.globals import titan_emoji_id, hunter_emoji_id, warlock_emoji_id, light_level_icon_emoji_id, tournament
from static.slashCommandOptions import choices_mode


class DestinyCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.classes = {
            "Warlock": warlock_emoji_id,
            "Hunter": hunter_emoji_id,
            "Titan": titan_emoji_id,
        }

    @cog_ext.cog_slash(
        name="poptimeline",
        description="Shows the Destiny 2 steam population timeline",
    )
    async def _poptimeline(self, ctx: SlashContext):
        season_dates = [
            ["2019-10-01", "Shadowkeep"],
            ["2019-12-10", "Season of Dawn"],
            ["2020-03-10", "Season of the Worthy"],
            ["2020-06-09", "Season of Arrivals"],
            ["2020-11-10", "Beyond Light"],
            ["2021-02-09", "Season of the Chosen"],
        ]
        other_dates = [
            ["2019-10-04", "GoS"],
            ["2019-10-29", "PoH"],
            ["2020-01-14", "Corridors of Time"],
            ["2020-04-21", "Guardian Games"],
            ["2020-06-06", "Almighty Live Event"],
            ["2020-08-11", "Solstice of Heroes"],
            ["2020-11-21", "DSC"],
        ]
        other_dates_lower = [
            ["2020-02-04", "Empyrean Foundation"],
            ["2020-07-07", "Moments of Triumph"],
        ]

        # reading data and preparing it
        data = pd.read_pickle('database/steamPlayerData.pickle')
        data['datetime'] = pd.to_datetime(data['datetime'])
        data['players'] = pd.to_numeric(data['players'])

        # Create figure and plot space
        fig, ax = plt.subplots(figsize=(20, 10))
        ax.yaxis.grid(True)

        # filling plot
        ax.plot(
            data['datetime'],
            data['players'],
            "darkred"
        )

        # Set title and labels for axes
        ax.set_title("Destiny 2 - Steam Player Count", fontweight="bold", size=30, pad=20)
        ax.set_xlabel("Date", fontsize=20)
        ax.set_ylabel("Players", fontsize=20)

        # adding nice lines to mark important events
        for dates in season_dates:
            date = datetime.datetime.strptime(dates[0], '%d/%m/%Y')
            ax.axvline(date, color="darkgreen")
            ax.text(date + datetime.timedelta(days=2), (max(data['players']) - min(data['players'])) * 1.02 + min(data['players']), dates[1], color="darkgreen", fontweight="bold", bbox=dict(facecolor='white', edgecolor='darkgreen', pad=4))
        for dates in other_dates:
            date = datetime.datetime.strptime(dates[0], '%d/%m/%Y')
            ax.axvline(date, color="mediumaquamarine")
            ax.text(date + datetime.timedelta(days=2), (max(data['players']) - min(data['players'])) * 0.95 + min(data['players']), dates[1], color="mediumaquamarine", bbox=dict(facecolor='white', edgecolor='mediumaquamarine', boxstyle='round'))
        for dates in other_dates_lower:
            date = datetime.datetime.strptime(dates[0], '%d/%m/%Y')
            ax.axvline(date, color="mediumaquamarine")
            ax.text(date + datetime.timedelta(days=2), (max(data['players']) - min(data['players'])) * 0.90 + min(data['players']), dates[1], color="mediumaquamarine", bbox=dict(facecolor='white', edgecolor='mediumaquamarine', boxstyle='round'))

        # saving file
        title = "players.png"
        plt.savefig(title)

        # sending them the file
        await ctx.send(file=discord.File(title))

        # delete file
        os.remove(title)


    @cog_ext.cog_slash(
        name="last",
        description="Stats for the last activity you played",
        options=[
            create_option(
                name="activity",
                description="The type of the activity",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="Raids",
                        value="4"
                    ),
                    create_choice(
                        name="Dungeon",
                        value="82"
                    ),
                    create_choice(
                        name="Story (including stuff like Presage)",
                        value="2"
                    ),
                    create_choice(
                        name="Strike",
                        value="3"
                    ),
                    create_choice(
                        name="Nightfall",
                        value="16"
                    ),
                    create_choice(
                        name="Everything PvE",
                        value="7"
                    ),
                    create_choice(
                        name="Trials",
                        value="84"
                    ),
                    create_choice(
                        name="Iron Banner",
                        value="19"
                    ),
                    create_choice(
                        name="Everything PvP",
                        value="5"
                    ),
                    create_choice(
                        name="Gambit",
                        value="63"
                    ),
                ]
            ),
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            ),
        ],
    )
    async def _last(self, ctx: SlashContext, **kwargs):
        await ctx.defer()
        user = await get_user_obj(ctx, kwargs)
        _, destinyID, system = await get_destinyID_and_system(ctx, user)
        if not destinyID:
            return

        # get data for the mode specified
        await updateDB(destinyID)
        data = await getLastActivity(destinyID, mode=kwargs["activity"])

        # make data pretty and send msg
        activity_name = (await getDestinyDefinition("DestinyActivityDefinition", data['directorActivityHash']))[2]
        embed = embed_message(
            f"{user.display_name}'s Last Activity",
            f"**{activity_name}{(' - ' + str(data['score']) + ' Points') if data['score'] > 0 else ''} - {str(datetime.timedelta(seconds=data['activityDurationSeconds']))}**",
            f"Date: {data['period'].strftime('%d/%m/%Y, %H:%M')} - InstanceID: {data['instanceID']}"
        )

        for player in data['entries']:
            player_data = [
                f"K: **{player['opponentsDefeated']}**, D: **{player['deaths']}**, A: **{player['assists']}**",
                f"K/D: **{round((player['opponentsDefeated'] / player['deaths']) if player['deaths'] > 0 else player['opponentsDefeated'], 2)}** {'(DNF)' if not player['completed'] else ''}",
                str(datetime.timedelta(seconds=player['timePlayedSeconds'])),
            ]

            # sometimes people dont have a class for some reason. Skipping that
            if player['characterClass'] == '':
                continue

            embed.add_field(name=f"{await get_emoji(self.client, self.classes[player['characterClass']])} {await getDestinyName(player['membershipID'], membershipType=player['membershipType'])} {await get_emoji(self.client, light_level_icon_emoji_id)} {player['lightLevel']}", value="\n".join(player_data), inline=True)

        await ctx.send(embed=embed)


    @cog_ext.cog_slash(
        name="challenges",
        description="Shows you the seasonal challenges and your completion status",
        options=[
            create_option(
                name="week",
                description="The specific week you want to see",
                option_type=4,
                required=False,
            ),
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            ),
        ],
    )
    async def _challenges(self, ctx: SlashContext, **kwargs):
        await ctx.defer()
        user = await get_user_obj(ctx, kwargs)
        author = ctx.author
        _, destinyID, system = await get_destinyID_and_system(ctx, user)
        if not destinyID:
            return

        # get seasonal challenge info
        seasonal_challenges = await getSeasonalChallengeInfo()
        index = list(seasonal_challenges)

        # get the week (or the default - whatever is first)
        week = f"Week {kwargs['week']}" if "week" in kwargs else ""
        if week not in seasonal_challenges:
            week = index[0]

        # get player triumphs
        user_triumphs = await getTriumphsJSON(destinyID)

        # send data and wait for new user input
        await self._send_challenge_info(user, author, week, seasonal_challenges, index, user_triumphs, ctx=ctx, message=None)


    async def _send_challenge_info(self, user, author, week, seasonal_challenges, index, user_triumphs, ctx=None, message=None):
        # this is a recursive commmand.

        # make data pretty
        embed = await self._get_challenge_info(user, week, seasonal_challenges, user_triumphs)

        # send message
        if not message:
            message = await ctx.send(embed=embed)
        else:
            await message.edit(embed=embed)

        # get current indexes - to look whether to add arrows to right
        current_index = index.index(week)
        max_index = len(index) - 1

        # add reactions
        if current_index > 0:
            await message.add_reaction("⬅")
        if current_index < max_index:
            await message.add_reaction("➡")

        # wait 60s for reaction
        def check(reaction_reaction, reaction_user):
            return (str(reaction_reaction.emoji) == "⬅" or str(reaction_reaction.emoji) == "➡") \
                   and (reaction_reaction.message.id == message.id) \
                   and (author == reaction_user)

        try:
            reaction, _ = await self.client.wait_for('reaction_add', check=check, timeout=60)
        except asyncio.TimeoutError:
            # clear reactions
            await message.clear_reactions()
        else:
            # clear reactions
            await message.clear_reactions()

            # recursively call this function
            new_index = index[current_index - 1] if str(reaction.emoji) == "⬅" else index[current_index + 1]
            await self._send_challenge_info(user, author, new_index, seasonal_challenges, index, user_triumphs, message=message)


    async def _get_challenge_info(self, user, week, seasonal_challenges, user_triumphs):
        """ Returns an embed for the specified week """
        embed = embed_message(
            f"{user.display_name}'s Seasonal Challenges - {week}"
        )

        # add the triumphs and what the user has done
        for triumph in seasonal_challenges[week]:
            user_triumph = user_triumphs[str(triumph["referenceID"])]

            # calculate completion rate
            rate = []
            for objective in user_triumph["objectives"]:
                rate.append(objective["progress"] / objective["completionValue"] if not objective["complete"] else 1)
            rate = sum(rate) / len(rate)

            # make emoji art for completion rate
            rate_text = "|"
            if rate > 0:
                rate_text += "🟩"
            else:
                rate_text += "🟥"
            if rate > 0.25:
                rate_text += "🟩"
            else:
                rate_text += "🟥"
            if rate > 0.5:
                rate_text += "🟩"
            else:
                rate_text += "🟥"
            if rate == 1:
                rate_text += "🟩"
            else:
                rate_text += "🟥"
            rate_text += "|"

            # add field to embed
            embed.add_field(name=f"""{triumph["name"]} {rate_text}""", value=triumph["description"], inline=False)

        return embed


    # todo better perm system
    @cog_ext.cog_slash(
        name="spoder",
        description="The better /spider command to show Spiders current inventory",
        options=[
            create_option(
                name="user",
                description="Requires elevated permissions",
                option_type=6,
                required=False
            ),
        ],
    )
    async def _spoder(self, ctx: SlashContext, **kwargs):
        await ctx.defer()
        user = await get_user_obj_admin(ctx, kwargs)
        if not user:
            return
        discordID = user.id
        _, destinyID, system = await get_destinyID_and_system(ctx, user)
        if not destinyID:
            return
        anyCharID = (await getCharacterList(destinyID))[1][0]

        # get and send spider inv
        materialtext = await getSpiderMaterials(discordID, destinyID, anyCharID)
        if 'embed' in materialtext:
            await ctx.send(embed=materialtext['embed'])
        elif materialtext['result']:
            await ctx.send(materialtext['result'])
        else:
            await ctx.send(materialtext['error'])


    @cog_ext.cog_slash(
        name="destiny",
        description="Gives you various destiny stats",
        options=[
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            )
        ]
    )
    async def _destiny(self, ctx: SlashContext, **kwargs):
        await ctx.defer()

        # get basic user data
        user = await get_user_obj(ctx, kwargs)
        _, destinyID, system = await get_destinyID_and_system(ctx, user)
        if not destinyID:
            return

        heatmap_url = f"https://chrisfried.github.io/secret-scrublandeux/guardian/{system}/{destinyID}"
        characterIDs, character_data = await getCharacterInfoList(destinyID)
        character_playtime = {}     # in seconds
        for characterID in characterIDs:
            character_playtime[characterID] = await getCharStats(destinyID, characterID, "secondsPlayed")

        embed = embed_message(
            f"{user.display_name}'s Destiny Stats",
            f"**Total Playtime:** {str(datetime.timedelta(seconds=sum(character_playtime.values())))} \n[Click to see your heatmap]({heatmap_url})",
            "For info on achievable discord roles, type !roles"
        )

        """ char info field """
        embed.add_field(name="⁣", value=f"__**Characters:**__", inline=False)
        for characterID in characterIDs:
            text = f"""Playtime: {str(datetime.timedelta(seconds=character_playtime[characterID]))} \n⁣\nPower: {int(await getCharStats(destinyID, characterID, "highestLightLevel")):,} \nActivities: {int(await getCharStats(destinyID, characterID, "activitiesCleared")):,} \nKills: {int(await getCharStats(destinyID, characterID, "kills")):,} \nDeaths: {int(await getCharStats(destinyID, characterID, "deaths")):,} \nEfficiency: {round(await getCharStats(destinyID, characterID, "efficiency"), 2)}"""
            embed.add_field(name=f"""{character_data[characterID]["class"]} ({character_data[characterID]["race"]} / {character_data[characterID]["gender"]})""", value=text, inline=True)

        """ triumph info field """
        embed.add_field(name="⁣", value=f"__**Triumphs:**__", inline=False)

        # get triumph data
        triumphs = await getProfile(destinyID, 900)
        embed.add_field(name="Lifetime Triumph Score", value=f"""{triumphs["profileRecords"]["data"]["lifetimeScore"]:,}""", inline=True)
        embed.add_field(name="Active Triumph Score", value=f"""{triumphs["profileRecords"]["data"]["activeScore"]:,}""", inline=True)
        embed.add_field(name="Legacy Triumph Score", value=f"""{triumphs["profileRecords"]["data"]["legacyScore"]:,}""", inline=True)

        # get triumph completion rate
        triumphs_data = triumphs["profileRecords"]["data"]["records"]
        triumphs_completed = 0
        triumphs_no_data = 0
        for triumph in triumphs_data.values():
            status = True
            if "objectives" in triumph:
                for part in triumph['objectives']:
                    status &= part['complete']
            elif "intervalObjectives" in triumph:
                for part in triumph['intervalObjectives']:
                    status &= part['complete']
            else:
                triumphs_no_data += 1
                continue
            if status:
                triumphs_completed += 1
        embed.add_field(name="Triumphs", value=f"{triumphs_completed} / {len(triumphs_data) - triumphs_no_data}", inline=True)

        # get seal completion rate
        seals, completed_seals = await getPlayerSeals(destinyID)
        embed.add_field(name="Seals", value=f"{len(completed_seals)} / {len(seals)}", inline=True)

        # collection completion data
        collections_data = (await getProfile(destinyID, 800))["profileCollectibles"]["data"]["collectibles"]
        collectibles_completed = 0
        for collectible in collections_data.values():
            if collectible['state'] & 1 == 0:
                collectibles_completed += 1
        embed.add_field(name="Collections", value=f"{collectibles_completed} / {len(collections_data)}", inline=True)

        await ctx.send(embed=embed)


    @cog_ext.cog_slash(
        name="stat",
        description="Shows you various Destiny 2 Stats",
        options=[
            create_option(
                name="name",
                description="The name of the leaderboard you want to see",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="Kills",
                        value="kills"
                    ),
                    create_choice(
                        name="Precision Kills",
                        value="precisionKills"
                    ),
                    create_choice(
                        name="Assists",
                        value="assists"
                    ),
                    create_choice(
                        name="Deaths",
                        value="deaths"
                    ),
                    create_choice(
                        name="Suicides",
                        value="suicides"
                    ),
                    create_choice(
                        name="KDA",
                        value="efficiency"
                    ),
                    create_choice(
                        name="Longest Kill Distance",
                        value="longestKillDistance"
                    ),
                    create_choice(
                        name="Average Kill Distance",
                        value="averageKillDistance"
                    ),
                    create_choice(
                        name="Total Kill Distance",
                        value="totalKillDistance"
                    ),
                    create_choice(
                        name="Longest Kill Spree",
                        value="longestKillSpree"
                    ),
                    create_choice(
                        name="Average Lifespan",
                        value="averageLifespan"
                    ),
                    create_choice(
                        name="Resurrections Given",
                        value="resurrectionsPerformed"
                    ),
                    create_choice(
                        name="Resurrections Received",
                        value="resurrectionsReceived"
                    ),
                    create_choice(
                        name="Number of Players Played With",
                        value="allParticipantsCount"
                    ),
                    create_choice(
                        name="Longest Single Life (in s)",
                        value="longestSingleLife"
                    ),
                    create_choice(
                        name="Orbs of Power Dropped",
                        value="orbsDropped"
                    ),
                    create_choice(
                        name="Orbs of Power Gathered",
                        value="orbsGathered"
                    ),
                    create_choice(
                        name="Time Played (in s)",
                        value="secondsPlayed"
                    ),
                    create_choice(
                        name="Activities Cleared",
                        value="activitiesCleared"
                    ),
                    create_choice(
                        name="Public Events Completed",
                        value="publicEventsCompleted"
                    ),
                    create_choice(
                        name="Heroic Public Events Completed",
                        value="heroicPublicEventsCompleted"
                    ),
                    create_choice(
                        name="Kills with: Super",
                        value="weaponKillsSuper"
                    ),
                    create_choice(
                        name="Kills with: Melee",
                        value="weaponKillsMelee"
                    ),
                    create_choice(
                        name="Kills with: Grenade",
                        value="weaponKillsGrenade"
                    ),
                    create_choice(
                        name="Kills with: Ability",
                        value="weaponKillsAbility"
                    )
                ]
            ),
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            )
        ]
    )
    async def _stat(self, ctx: SlashContext, **kwargs):
        await ctx.defer()

        # get basic user data
        user = await get_user_obj(ctx, kwargs)
        _, destinyID, system = await get_destinyID_and_system(ctx, user)
        if not destinyID:
            return

        # get stat
        stat = await getIntStat(destinyID, kwargs["name"])
        await ctx.send(embed=embed_message(
            f"{user.display_name}'s Stat Info",
            f"Your `{kwargs['name']}` stat is currently at **{stat:,}**"
        ))


class ClanActivitiesCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

        # edge_list = [person, size, size_desc, display_names, colors]
        self.edge_list = []
        self.ignore = []


    @cog_ext.cog_slash(
        name="clanactivity",
        description="Shows information about who from the clan plays with whom (Default: in the last 7 days)",
        options=[
            create_option(
                name="mode",
                description="You can restrict the game mode",
                option_type=3,
                required=False,
                choices=choices_mode
            ),
            create_option(
                name="starttime",
                description="Format: 'DD/MM/YY' - You can restrict the start-time (lower cutoff)",
                option_type=3,
                required=False
            ),
            create_option(
                name="endtime",
                description="Format: 'DD/MM/YY' - You can restrict the end-time (higher cutoff)",
                option_type=3,
                required=False
            ),
            create_option(
                name="user",
                description="The name of the user you want to highlight",
                option_type=6,
                required=False
            )
        ]
    )
    async def _clanactivity(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)
        _, orginal_user_destiny_id, system = await get_destinyID_and_system(ctx, user)
        if not orginal_user_destiny_id:
            return

        # get params
        mode = int(kwargs["mode"]) if "mode" in kwargs else 0
        start_time = await verify_time_input(ctx, kwargs["starttime"]) if "starttime" in kwargs else datetime.datetime.now() - datetime.timedelta(days=7)
        if not start_time:
            return
        end_time = await verify_time_input(ctx, kwargs["endtime"]) if "endtime" in kwargs else datetime.datetime.now()
        if not end_time:
            return

        # this might take a sec
        await ctx.defer()

        # get clanmembers
        self.clan_members = await getClanMembers(self.client)
        self.activities_from_user_who_got_looked_at = {}
        self.friends = {}

        result = await asyncio.gather(*[self._handle_members(destinyID, mode, start_time, end_time, user.display_name) for destinyID in self.clan_members])
        for res in result:
            if res is not None:
                destinyID = res[0]

                self.activities_from_user_who_got_looked_at[destinyID] = res[1]
                self.friends[destinyID] = res[2]

        data_temp = []
        for destinyID in self.friends:
            for friend in self.friends[destinyID]:
                # data = [destinyID1, destinyID2, number of activities together]
                data_temp.append([int(str(destinyID)[-9:]), int(str(friend)[-9:]), self.friends[destinyID][friend]])

        data = np.array(data_temp)
        del data_temp

        # getting the display names, colors for users in discord, size of blob
        await asyncio.gather(*[self._prep_data(destinyID, orginal_user_destiny_id) for destinyID in self.clan_members])

        # building the network graph
        net = Network()

        # adding nodes
        # edge_list = [person, size, size_desc, display_names, colors]
        for edge_data in self.edge_list:
            net.add_node(int(str(edge_data[0])[-9:]), value=edge_data[1], title=edge_data[2], label=edge_data[3], color=edge_data[4])

        # adding edges with data = [user1, user2, number of activities together]
        with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 5) as pool:
            futurelist = [pool.submit(self._add_edge, net, edge) for edge in data]
            for _ in concurrent.futures.as_completed(futurelist):
                pass

        net.barnes_hut(gravity=-200000, central_gravity=0.3, spring_length=200, spring_strength=0.005, damping=0.09, overlap=0)
        net.show_buttons(filter_=["physics"])

        # saving the file
        title = user.display_name + ".html"
        net.save_graph(title)

        # letting user know it's done
        await ctx.send(embed=embed_message(
            f"{user.display_name}'s Friends",
            f"Click the download button below and open the file with your browser to view your Network",
            f"The file may load for a while, that's normal."
        ))
        # sending them the file
        await ctx.channel.send(file=discord.File(title))

        # delete file
        os.remove(title)


    async def _handle_members(self, destinyID, mode, start_time, end_time, name):
        # getting the activities for the
        result = await self._return_activities(destinyID, mode, start_time, end_time)
        activities_from_user_who_got_looked_at = len(result[1])

        # getting the friends from his activities
        destinyIDs_friends = []
        for ID in result[1]:
            result = await self._return_friends(destinyID, ID)
            destinyIDs_friends.extend(result)
        friends = dict(Counter(destinyIDs_friends))

        return [destinyID, activities_from_user_who_got_looked_at, friends]


    async def _return_activities(self, destinyID, mode, start_time, end_time):
        destinyID = int(destinyID)

        # get all activities
        activities = await getActivityHistory(destinyID, mode=mode, start_time=start_time, end_time=end_time)

        list_of_activities = []
        for instanceID in activities:
            list_of_activities.append(instanceID)

        return [destinyID, set(list_of_activities)]


    async def _return_friends(self, destinyID, instanceID):
        # list in which the connections are saved
        friends = []

        # get instance id info
        data = await getPgcrActivitiesUsersStats(instanceID)
        for player in data:
            friendID = player[1]

            # only look at clan members
            if friendID in self.clan_members:
                # doesn't make sense to add yourself
                if friendID != destinyID:
                    friends.append(friendID)

        # sort and count friends
        return friends


    async def _prep_data(self, destinyID, orginal_user_destiny_id):
        display_name = await self._get_display_name(destinyID)

        size = self.activities_from_user_who_got_looked_at[destinyID] * 50
        size_desc = str(self.activities_from_user_who_got_looked_at[destinyID]) + " Activities"

        colors = "#850404" if orginal_user_destiny_id == destinyID else "#006aff"

        # edge_list = [person, size, size_desc, display_names, colors]
        self.edge_list.append([destinyID, size, size_desc, display_name, colors])


    async def _get_display_name(self, destinyID):
        display_name = (await getProfile(destinyID, 100))
        return display_name["profile"]["data"]["userInfo"]["displayName"] if display_name else "Unknown Name"


    def _add_edge(self, network, edge):
        src = int(edge[0])
        dst = int(edge[1])
        value = int(edge[2])

        # add the edge
        try:
            network.add_edge(dst, src, value=value, title=value, physics=True)
        except Exception:
            print("error adding node")


class MysticCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    def names(self, userdict):
        return '\n'.join(map(lambda p: c.name if (c := self.client.get_user(p['id'])) else "InvalidUser", userdict))


    # todo can we add a good permission sysstem here too?
    @cog_ext.cog_subcommand(
        base="mystic",
        base_description="Everything concerning Mystic's abandoned carry list. Tbf he said he tried ¯\_(ツ)_/¯",
        name="list",
        description="Displays the current list",
    )
    async def _list(self, ctx: SlashContext):
        with open('database/mysticlist.json', 'r+') as mlist:
            players = json.load(mlist)

        embed = embed_message(
            'Mystic List',
            f'The following users are currently in the list:'
        )
        embed.add_field(name="Users", value=self.names(players), inline=True)

        await ctx.send(embed=embed)


    # todo can we add a good permission sysstem here too?
    @cog_ext.cog_subcommand(
        base="mystic",
        base_description="Everything concerning Mystic's abandoned carry list. Tbf he said he tried ¯\_(ツ)_/¯",
        name="add",
        description="Add a user to the list",
        options=[
            create_option(
                name="user",
                description="Requires elevated permissions",
                option_type=6,
                required=False
            )
        ]
    )
    async def _add(self, ctx: SlashContext, **kwargs):
        # allow mystic himself
        user = await get_user_obj_admin(ctx, kwargs, allowed_users=[211838266834550785])
        if not user:
            return

        with open('database/mysticlist.json', 'r') as mlist:
            players = json.load(mlist)

        # add new player
        players.append({'name': user.display_name, 'id': user.id})

        with open('commands/mysticlog.log', 'a') as mlog:
            mlog.write(f'\n{ctx.author.name} added {user.name}')

        with open('database/mysticlist.json', 'w') as mlist:
            json.dump(players, mlist)

        embed = embed_message(
            'Mystic List',
            f'Added {user.name} to the mystic list, it now has:'
        )
        embed.add_field(name="Users", value=self.names(players), inline=True)

        await ctx.send(embed=embed)


    # todo can we add a good permission sysstem here too?
    @cog_ext.cog_subcommand(
        base="mystic",
        base_description="Everything concerning Mystic's abandoned carry list. Tbf he said he tried ¯\_(ツ)_/¯",
        name="remove",
        description="Remove a user from the list",
        options=[
            create_option(
                name="user",
                description="Requires elevated permissions",
                option_type=6,
                required=False
            )
        ]
    )
    async def _remove(self, ctx: SlashContext, **kwargs):
        # allow mystic himself
        user = await get_user_obj_admin(ctx, kwargs, allowed_users=[211838266834550785])
        if not user:
            return

        with open('database/mysticlist.json', 'r') as mlist:
            players = json.load(mlist)

        if len(player := list(filter(lambda muser: muser['id'] == user.id, players))) == 1:
            # remove player
            players.remove(player[0])
            with open('commands/mysticlog.log', 'a') as mlog:
                mlog.write(f'\n{ctx.author.name} removed {user.name}')

            with open('database/mysticlist.json', 'w+') as mlist:
                json.dump(players, mlist)

            embed = embed_message(
                'Mystic List',
                f'Removed {user.name} from the mystic list, it now has:'
            )
            embed.add_field(name="Users", value=self.names(players), inline=True)

            await ctx.send(embed=embed)
            return

        await ctx.send(embed=embed_message(
            'Mystic List',
            f"User {user.name} was not found in the player list"
        ))


class RankCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.stats = {
            "mobility": 2996146975,
            "resilience": 392767087,
            "recovery": 1943323491,
            "discipline": 1735777505,
            "intellect": 144602215,
            "strength": 4244567218
        }


    @cog_ext.cog_slash(
        name="rank",
        description="Display Destiny 2 leaderboard for clanmates",
        options=[
            create_option(
                name="leaderboard",
                description="The name of the leaderboard you want to see",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="Join-Date of this Discord Server",
                        value="discordjoindate"
                    ),
                    create_choice(
                        name="Total Playtime",
                        value="totaltime"
                    ),
                    create_choice(
                        name="Max. Power Level",
                        value="maxpower"
                    ),
                    create_choice(
                        name="Vault Space Used",
                        value="vaultspace"
                    ),
                    create_choice(
                        name="Orbs of Power Generated",
                        value="orbs"
                    ),
                    create_choice(
                        name="Melee Kills",
                        value="meleekills"
                    ),
                    create_choice(
                        name="Super Kills",
                        value="superkills"
                    ),
                    create_choice(
                        name="Grenade Kills",
                        value="grenadekills"
                    ),
                    create_choice(
                        name="Deaths",
                        value="deaths"
                    ),
                    create_choice(
                        name="Suicides",
                        value="suicides"
                    ),
                    create_choice(
                        name="Kills",
                        value="kills"
                    ),
                    create_choice(
                        name="Raids Done",
                        value="raids"
                    ),
                    create_choice(
                        name="Raid Time",
                        value="raidtime"
                    ),
                    create_choice(
                        name="Weapon Kills",
                        value="weapon"
                    ),
                    create_choice(
                        name="Weapon Precision Kills",
                        value="weaponprecision"
                    ),
                    create_choice(
                        name="% Weapon Precision Kills",
                        value="weaponprecisionpercent"
                    ),
                    create_choice(
                        name="Enhancement Cores",
                        value="enhancementcores"
                    ),
                    create_choice(
                        name="Forges Done",
                        value="forges"
                    ),
                    create_choice(
                        name="AFK Forges Done",
                        value="afkforges"
                    ),
                    create_choice(
                        name="Active Triumph Score",
                        value="activetriumphs"
                    ),
                    create_choice(
                        name="Legacy Triumph Score",
                        value="legacytriumphs"
                    ),
                    create_choice(
                        name="Triumph Score",
                        value="triumphs"
                    ),
                ]
            ),
            create_option(
                name="arg",
                description="Depending on which leaderboard you want to see, you might need to add an additional argument",
                option_type=3,
                required=False
            ),
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            )
        ]
    )
    async def _rank(self, ctx: SlashContext, **kwargs):
        await ctx.defer()

        user = await get_user_obj(ctx, kwargs)
        leaderboard = kwargs["leaderboard"]
        item_name = None
        item_hashes = None

        # if a weapon leaderboard is asked for
        if leaderboard in ["weapon", "weaponprecision", "weaponprecisionpercent"]:
            if "arg" in kwargs:
                item_name, item_hashes = await searchForItem(ctx, kwargs["arg"])
                if not item_name:
                    return

            # send error message and exit
            else:
                await ctx.send("Error: Please specify a weapon in the command argument `arg`", hidden=True)
                return

        # calculate the leaderboard
        embed = await self._handle_users(leaderboard, user.display_name, ctx.guild, item_hashes, item_name)

        if embed:
            await ctx.send(embed=embed)


    async def _handle_users(self, stat, display_name, guild, extra_hash, extra_name):
        # init DF. "stat_sort" is only here, since I want to save numbers fancy (1,000,000) and that is a string and not an int so sorting wont work
        data = pd.DataFrame(columns=["member", "stat", "stat_sort"])

        # loop through the clan members
        clan_members = (await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"))["Response"][
            "results"]
        results = await asyncio.gather(*[self._handle_user(stat, member, guild, extra_hash, extra_name) for member in clan_members])
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


    async def _handle_user(self, stat, member, guild, extra_hash, extra_name):
        destinyID = int(member["destinyUserInfo"]["membershipId"])
        discordID = await lookupDiscordID(destinyID)
        sort_by_ascending = False

        if not await getToken(discordID):
            return None

        # catch people that are in the clan but not in discord, shouldn't happen tho
        try:
            discord_member = guild.get_member(discordID)
            name = discord_member.display_name
        except Exception:
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
            result_sort = self._add_stats(json, "secondsPlayed") / 60 / 60
            result = f"{result_sort:,}"

        elif stat == "orbs":
            leaderboard_text = "Top Clanmembers by PvE Orbs Generated"
            stat_text = "Orbs"

            json = await getStats(destinyID)
            result_sort = self._add_stats(json, "orbsDropped", scope="pve")
            result = f"{result_sort:,}"

        elif stat == "meleekills":
            leaderboard_text = "Top Clanmembers by D2 PvE Meleekills"
            stat_text = "Kills"

            json = await getStats(destinyID)
            result_sort = self._add_stats(json, "weaponKillsMelee", scope="pve")
            result = f"{result_sort:,}"

        elif stat == "superkills":
            leaderboard_text = "Top Clanmembers by D2 PvE Superkills"
            stat_text = "Kills"

            json = await getStats(destinyID)
            result_sort = self._add_stats(json, "weaponKillsSuper", scope="pve")
            result = f"{result_sort:,}"

        elif stat == "grenadekills":
            leaderboard_text = "Top Clanmembers by D2 PvE Grenadekills"
            stat_text = "Kills"

            json = await getStats(destinyID)
            result_sort = self._add_stats(json, "weaponKillsGrenade", scope="pve")
            result = f"{result_sort:,}"

        elif stat == "deaths":
            leaderboard_text = "Top Clanmembers by D2 PvE Deaths"
            stat_text = "Deaths"

            json = await getStats(destinyID)
            result_sort = self._add_stats(json, "deaths", scope="pve")
            result = f"{result_sort:,}"

        elif stat == "suicides":
            leaderboard_text = "Top Clanmembers by D2 PvE Suicides"
            stat_text = "Suicides"

            json = await getStats(destinyID)
            result_sort = self._add_stats(json, "suicides", scope="pve")
            result = f"{result_sort:,}"

        elif stat == "kills":
            leaderboard_text = "Top Clanmembers by D2 PvE Kills"
            stat_text = "Kills"

            json = await getStats(destinyID)
            result_sort = self._add_stats(json, "kills", scope="pve")
            result = f"{result_sort:,}"

        elif stat == "maxpower":
            # TODO efficiency
            if not await getToken(discordID):
                return None

            leaderboard_text = "Top Clanmembers by D2 Maximum Reported Power"
            stat_text = "Power"

            artifact_power = (await getArtifact(destinyID))["powerBonus"]

            items = await getCharacterGearAndPower(destinyID)
            items = self._sort_gear_by_slot(items)

            results = await asyncio.gather(*[self._get_highest_item_light_level(slot) for slot in items])

            total_power = 0
            for ret in results:
                total_power += ret
            total_power /= 8

            result_sort = int(total_power + artifact_power)
            result = f"{int(total_power):,} + {artifact_power:,}"

        elif stat == "vaultspace":
            # todo doesnt work all the time
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
            result_sort = int((await self._add_activity_stats(destinyID, raidHashes, "activitySecondsPlayed")) / 60 / 60)
            result = f"{result_sort:,}"

        elif stat == "forges":
            leaderboard_text = "Top Clanmembers by D2 Forge Completions"
            stat_text = "Total"

            result_sort = 0
            farmed_runs = 0
            for _, kills in await getForges(destinyID):
                if kills > 0:
                    result_sort += 1
                else:
                    farmed_runs += 1

            result = f"{result_sort:,} + {farmed_runs:,} AFK runs"

        elif stat == "afkforges":
            leaderboard_text = "Top Clanmembers by D2 AFK Forge Completions"
            stat_text = "Total"

            farmed_runs = 0
            result_sort = 0
            for _, kills in await getForges(destinyID):
                if kills > 0:
                    farmed_runs += 1
                else:
                    result_sort += 1

            result = f"{farmed_runs:,} + {result_sort:,} AFK runs"

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
            result = f"{round(result_sort * 100, 2)}%"

        elif stat == "activetriumphs":
            leaderboard_text = f"Top Clanmembers by D2 Active Triumph Score"
            stat_text = "Score"

            result_sort = (await getProfile(destinyID, 900))["profileRecords"]["data"]["activeScore"]
            result = f"{result_sort:,}"

        elif stat == "legacytriumphs":
            leaderboard_text = f"Top Clanmembers by D2 Legacy Triumph Score"
            stat_text = "Score"

            result_sort = (await getProfile(destinyID, 900))["profileRecords"]["data"]["legacyScore"]
            result = f"{result_sort:,}"

        elif stat == "triumphs":
            leaderboard_text = f"Top Clanmembers by D2 Lifetime Triumph Score"
            stat_text = "Score"

            result_sort = (await getProfile(destinyID, 900))["profileRecords"]["data"]["lifetimeScore"]
            result = f"{result_sort:,}"

        else:
            return

        return [name, result, result_sort, leaderboard_text, stat_text, sort_by_ascending]


    async def _add_activity_stats(self, destinyID, hashes, stat):
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
            except Exception:
                pass

        return result_sort


    async def _get_highest_item_light_level(self, items):
        max_power = 0

        for item in items:
            if item['lightlevel'] > max_power:
                max_power = item['lightlevel']
        return max_power


    def _sort_gear_by_slot(self, items):
        helmet = []  # 3448274439
        gauntlet = []  # 3551918588
        chest = []  # 14239492
        leg = []  # 20886954
        class_item = []  # 1585787867

        kinetic = []  # 1498876634
        energy = []  # 2465295065
        power = []  # 953998645

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


    def _add_stats(self, json, stat, scope="all"):
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
                result_sort += int(
                    json["mergedDeletedCharacters"]["results"]["allPvE"]["allTime"][stat]["basic"]["value"])
            except:
                pass
        elif scope == "pvp":
            result_sort = int(json["mergedAllCharacters"]["results"]["allPvP"]["allTime"][stat]["basic"]["value"])
            try:
                result_sort += int(
                    json["mergedDeletedCharacters"]["results"]["allPvP"]["allTime"][stat]["basic"]["value"])
            except:
                pass
        return result_sort


class WeaponCommands(commands.Cog):
    def __init__(self, client):
        self.client = client


    @cog_ext.cog_slash(
        name="weapon",
        description="Shows weapon stats for the specified weapon with in-depth customisation",
        options=[
            create_option(
                name="weapon",
                description="The name of the weapon you want to see stats for",
                option_type=3,
                required=True,
            ),
            create_option(
                name="stat",
                description="Which stat you want to see for the weapon",
                option_type=3,
                required=False,
                choices=[
                    create_choice(
                        name="Kills (default)",
                        value="kills"
                    ),
                    create_choice(
                        name="Precision Kills",
                        value="precisionkills"
                    ),
                    create_choice(
                        name="% Precision Kills",
                        value="precisionkillspercent"
                    ),
                ]
            ),
            create_option(
                name="graph",
                description="Default: 'False' - See a timeline of your weapon usage instead of an overview of key stats",
                option_type=5,
                required=False,
            ),
            create_option(
                name="class",
                description="You can restrict the class where the weapon stats count",
                option_type=3,
                required=False,
                choices=[
                    create_choice(
                        name="Warlock",
                        value="2271682572"
                    ),
                    create_choice(
                        name="Hunter",
                        value="671679327"
                    ),
                    create_choice(
                        name="Titan",
                        value="3655393761"
                    ),
                ]
            ),
            create_option(
                name="starttime",
                description="Format: 'DD/MM/YY' - You can restrict the time from when the weapon stats start counting",
                option_type=3,
                required=False
            ),
            create_option(
                name="endtime",
                description="Format: 'DD/MM/YY' - You can restrict the time up until which the weapon stats count",
                option_type=3,
                required=False
            ),
            create_option(
                name="mode",
                description="You can restrict the game mode where the weapon stats count",
                option_type=3,
                required=False,
                choices=choices_mode
            ),
            create_option(
                name="activityhash",
                description="You can restrict the activity where the weapon stats count (advanced)",
                option_type=4,
                required=False
            ),
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            ),
        ]
    )
    async def _weapon(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)
        _, destinyID, system = await get_destinyID_and_system(ctx, user)
        if not destinyID:
            return

        # get other params
        stat, graph, character_class, mode, activity_hash, starttime, endtime = await self._compute_params(ctx, kwargs)
        if not stat:
            return

        # might take a sec
        await ctx.defer()

        # get weapon info
        weapon_name, weapon_hashes = await searchForItem(ctx, kwargs["weapon"])
        if not weapon_name:
            return

        # get the char class if that is asked for
        charID = await getCharacterID(destinyID, character_class) if character_class else None

        # get all weapon infos
        kwargs = {
            "characterID": charID,
            "mode": mode,
            "activityID": activity_hash,
            "start": starttime,
            "end": endtime
        }

        # loop through every variant of the weapon and add that together
        result = []
        for entry in weapon_hashes:
            result.extend(await getWeaponInfo(destinyID, entry, **{k: v for k, v in kwargs.items() if v is not None}))

        # throw error if no weapon
        if not result:
            await ctx.send(embed=embed_message(
                "Error",
                f'No weapon stats found for {weapon_name}'
            ))
            return

        # either text
        if not graph:
            # get data
            kills = 0
            precision_kills = 0
            max_kills = 0
            max_kills_id = None
            for instanceID, uniqueweaponkills, uniqueweaponprecisionkills in result:
                kills += uniqueweaponkills
                precision_kills += uniqueweaponprecisionkills
                if uniqueweaponkills > max_kills:
                    max_kills = uniqueweaponkills
                    max_kills_id = instanceID
            percent_precision_kills = precision_kills / kills if kills else 0
            avg_kills = kills / len(result)
            res = await getPgcrActivity(max_kills_id)
            max_kills_date = res[3]
            max_kills_mode = (await getDestinyDefinition("DestinyActivityModeDefinition", res[5]))[2]
            max_kills_name = (await getDestinyDefinition("DestinyActivityDefinition", res[2]))[2]

            # make and post embed
            embed = embed_message(
                f"{weapon_name} stats for {user.display_name}",
                f""
            )
            embed.add_field(name="Total Kills", value=f"**{kills:,}**", inline=True)
            embed.add_field(name="Total Precision Kills", value=f"**{precision_kills:,}**", inline=True)
            embed.add_field(name="% Precision Kills", value=f"**{round(percent_precision_kills * 100, 2)}%**",
                            inline=True)
            embed.add_field(name="Average Kills", value=f"**{round(avg_kills, 2)}**\nIn {len(result)} Activities",
                            inline=True)
            embed.add_field(name="Maximum Kills",
                            value=f"**{max_kills:,}**\nIn Activity ID: {max_kills_id}\n{max_kills_mode} - {max_kills_name}\nOn: {max_kills_date.strftime('%d/%m/%y')}",
                            inline=True)
            await ctx.send(embed=embed)

        # or do a graph
        else:
            # get the time instead of the instance id and sort it so the earliest date is first
            weapon_hashes = []
            for instanceID, uniqueweaponkills, uniqueweaponprecisionkills in result:
                instance_time = (await getPgcrActivity(instanceID))[3]
                weapon_hashes.append((instance_time, uniqueweaponkills, uniqueweaponprecisionkills))
            weapon_hashes = sorted(weapon_hashes, key=lambda x: x[0])

            # get clean, relevant data in a DF. easier for the graph later
            df = pd.DataFrame(columns=["datetime", "statistic"])
            name = ""
            statistic1 = 0
            statistic2 = 0
            time = weapon_hashes[0][0]
            for instance_time, uniqueweaponkills, uniqueweaponprecisionkills in weapon_hashes:
                if instance_time.date() == time.date():
                    if stat == "kills":
                        statistic1 += uniqueweaponkills
                        name = "Kills"
                    elif stat == "precisionkills":
                        statistic1 += uniqueweaponprecisionkills
                        name = "Precision Kills"
                    elif stat == "precisionkillspercent":
                        statistic1 += uniqueweaponkills
                        statistic2 += uniqueweaponprecisionkills
                        name = "% Precision Kills"
                    time = instance_time
                else:
                    # append to DF
                    entry = {
                        'datetime': time.date(),
                        'statistic': statistic2 / statistic1 if stat == "precisionkillspercent" else statistic1
                    }
                    df = df.append(entry, ignore_index=True)

                    # save new data
                    if stat == "kills":
                        statistic1 = uniqueweaponkills
                        name = "Kills"
                    elif stat == "precisionkills":
                        statistic1 = uniqueweaponprecisionkills
                        name = "Precision Kills"
                    elif stat == "precisionkillspercent":
                        statistic1 = uniqueweaponkills
                        statistic2 = uniqueweaponprecisionkills
                        name = "% Precision Kills"
                    time = instance_time

            # append to DF
            entry = {
                'datetime': time,
                'statistic': statistic2 / statistic1 if stat == "precisionkillspercent" else statistic1
            }
            df = df.append(entry, ignore_index=True)

            # convert to correct file types
            df['datetime'] = pd.to_datetime(df['datetime'])
            df['statistic'] = pd.to_numeric(df['statistic'])

            # building the graph
            # Create figure and plot space
            fig, ax = plt.subplots(figsize=(20, 10))
            ax.yaxis.grid(True)

            # filling bar chart
            ax.bar(
                df['datetime'],
                df['statistic'],
                color="#45b6fe"
            )

            # Set title and labels for axes
            ax.set_title(f"{weapon_name} stats for {user.display_name}", fontweight="bold", size=30, pad=20)
            ax.set_xlabel("Date", fontsize=20)
            ax.set_ylabel(name, fontsize=20)

            # saving file
            title = "weapon.png"
            plt.savefig(title)

            # sending them the file
            await ctx.send(file=discord.File(title))

            # delete file
            os.remove(title)


    @cog_ext.cog_slash(
        name="topweapons",
        description="Shows your top weapon ranking with in-depth customisation",
        options=[
            create_option(
                name="weapon",
                description="If you want a specific weapon to be included on the ranking",
                option_type=3,
                required=False,
            ),
            create_option(
                name="stat",
                description="Which stat you want to see for the weapon ranking",
                option_type=3,
                required=False,
                choices=[
                    create_choice(
                        name="Kills (default)",
                        value="kills"
                    ),
                    create_choice(
                        name="Precision Kills",
                        value="precisionkills"
                    ),
                    create_choice(
                        name="% Precision Kills",
                        value="precisionkillspercent"
                    ),
                ]
            ),
            create_option(
                name="class",
                description="You can restrict the class where the weapon stats count",
                option_type=3,
                required=False,
                choices=[
                    create_choice(
                        name="Warlock",
                        value="2271682572"
                    ),
                    create_choice(
                        name="Hunter",
                        value="671679327"
                    ),
                    create_choice(
                        name="Titan",
                        value="3655393761"
                    ),
                ]
            ),
            create_option(
                name="starttime",
                description="Format: 'DD/MM/YY' - You can restrict the time from when the weapon stats start counting",
                option_type=3,
                required=False
            ),
            create_option(
                name="endtime",
                description="Format: 'DD/MM/YY' - You can restrict the time up until which the weapon stats count",
                option_type=3,
                required=False
            ),
            create_option(
                name="mode",
                description="You can restrict the game mode where the weapon stats count",
                option_type=3,
                required=False,
                choices=choices_mode
            ),
            create_option(
                name="activityhash",
                description="You can restrict the activity where the weapon stats count (advanced)",
                option_type=4,
                required=False
            ),
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            ),
        ]
    )
    async def _topweapons(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)
        _, destinyID, system = await get_destinyID_and_system(ctx, user)
        if not destinyID:
            return

        # get other params
        stat, _, character_class, mode, activity_hash, starttime, endtime = await self._compute_params(ctx, kwargs)
        if not stat:
            return

        # this might take a sec
        await ctx.defer()

        # get the real weapon name if that param is given
        weapon_name = None
        if "weapon" in kwargs:
            weapon_name, _ = await searchForItem(ctx, kwargs["weapon"])
            if not weapon_name:
                return

        # get the char class if that is asked for
        charID = await getCharacterID(destinyID, character_class) if character_class else None

        # get all weaponID infos
        kwargs = {
            "characterID": charID,
            "mode": mode,
            "activityID": activity_hash,
            "start": starttime,
            "end": endtime
        }
        result = await getTopWeapons(destinyID, **{k: v for k, v in kwargs.items() if v is not None})

        # loop through that and get data
        data = []
        for weaponID, uniqueweaponkills, uniqueweaponprecisionkills in result:
            # get the name
            weapon_data = [(await getDestinyDefinition("DestinyInventoryItemDefinition", weaponID))[2]]

            if stat == "kills":
                statistic = uniqueweaponkills
                weapon_data.append(statistic)
                weapon_data.append(f"{statistic:,}")
            elif stat == "precisionkills":
                statistic = uniqueweaponprecisionkills
                weapon_data.append(statistic)
                weapon_data.append(f"{statistic:,}")
            elif stat == "precisionkillspercent":
                statistic = uniqueweaponkills / uniqueweaponprecisionkills if uniqueweaponprecisionkills != 0 else 0
                weapon_data.append(statistic)
                weapon_data.append(f"{round(statistic * 100, 2)}%")

            data.append(tuple(weapon_data))

        # sort by index specified
        sorted_data = sorted(data, key=lambda x: x[1], reverse=True)

        # get the data for the embed
        i = 0
        ranking = []
        found = False if weapon_name else True
        for name, _, statistic in sorted_data:
            i += 1
            if len(ranking) < 12:
                # setting a flag if name is in list
                if weapon_name == name:
                    found = True
                    ranking.append(write_line(i, f"""[{name}]""", stat.capitalize(), statistic))
                else:
                    ranking.append(write_line(i, name, stat.capitalize(), statistic))

            # looping through rest until original user is found
            elif (len(ranking) >= 12) and (not found):
                # adding only this name
                if weapon_name == name:
                    ranking.append("...")
                    ranking.append(write_line(i, name, stat.capitalize(), statistic))
                    found = True
                    break

            else:
                break

        # write "0" as data, since it is not in there
        if not found:
            ranking.append("...")
            ranking.append(write_line(i, weapon_name, stat.capitalize(), 0))

        # make and post embed
        embed = embed_message(
            f"Top Weapons for {user.display_name}",
            "\n".join(ranking),
        )
        await ctx.send(embed=embed)


    async def _compute_params(self, ctx, kwargs):
        # set default values for the args
        stat = kwargs["stat"] if "stat" in kwargs else "kills"
        graph = bool(kwargs["graph"]) if "graph" in kwargs else False
        character_class = int(kwargs["class"]) if "class" in kwargs else None
        mode = int(kwargs["mode"]) if "mode" in kwargs else 0
        try:
            activity_hash = int(kwargs["activityhash"]) if "activityhash" in kwargs else None
        except ValueError:
            await ctx.send("Error: The activityhash parameters must be an integer", hidden=True)
            return None, None, None, None, None, None, None

        # make sure the times are valid
        starttime = await verify_time_input(ctx, kwargs["starttime"]) if "starttime" in kwargs else datetime.datetime.min
        if not starttime:
            return None, None, None, None, None, None, None
        endtime = await verify_time_input(ctx, kwargs["endtime"]) if "endtime" in kwargs else datetime.datetime.now()
        if not endtime:
            return None, None, None, None, None, None, None

        return stat, graph, character_class, mode, activity_hash, starttime, endtime


class TournamentCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.creator = None


    @cog_ext.cog_subcommand(
        base="tournament",
        base_description="Everything you need for in-house PvP tournaments",
        name="create",
        description="Opens up registration. Can only be used if no other tournament is currently running",
    )
    async def _create(self, ctx: SlashContext):
        # check if tourn already exists
        message = await get_persistent_message(self.client, "tournament", ctx.guild.id)
        if message:
            await ctx.send("Error: A tournament already exists. \nPlease wait until it is completed and then try again", hidden=True)
            return

        # get the tourn channel id
        channel = (await get_persistent_message(self.client, "tournamentChannel", ctx.guild.id)).channel

        # make registration message
        embed = embed_message(
            "Registration",
            f"{ctx.author.display_name} startet a tournament!\nTo enter it, please react accordingly"
        )
        await make_persistent_message(self.client, "tournament", ctx.guild.id, channel.id, reaction_id_list=tournament, message_embed=embed)

        # to remember who started the tournament, we set ctx.author as the message author
        self.creator = ctx.author

        # let user know
        await ctx.send(embed=embed_message(
            "Success",
            f"Registration for the tournament has started, visit {channel.mention} to join the fun!"
        ))


    @cog_ext.cog_subcommand(
        base="tournament",
        base_description="Everything you need for in-house PvP tournaments",
        name="start",
        description="Starts the tournament. Can only be used by the user who used '/tournament create' or an Admin",
    )
    async def _start(self, ctx: SlashContext):
        # check if tourn exists
        message = await get_persistent_message(self.client, "tournament", ctx.guild.id)
        if not message:
            await ctx.send("Error: You need to start the registration by using `/tournament create` first", hidden=True)
            return

        # check if author has permissions to start
        if not (message.author == ctx.author) and not (await has_elevated_permissions(ctx.author, ctx.guild)):
            await ctx.send("Error: Only admins and the tournament creator can start the tournament", hidden=True)
            return

        # check that at least two people (3, since bot counts too) have reacted and get the users
        for reaction in message.reactions:
            if reaction.emoji.id in tournament:
                if reaction.count < 3:
                    await ctx.send("Error: At least two people need to sign up", hidden=True)
                    return
                participants = []
                async for user in reaction.users():
                    if not user.bot:
                        participants.append(user)

        # start the tourn and wait for it to play out
        await ctx.send(embed=embed_message(
            "Success",
            "The tournament is now starting"
        ))
        winner = await startTournamentEvents(self.client, message, message.channel, participants)

        # delete registration message
        channel = message.channel
        await delete_persistent_message(message, "tournament", ctx.guild.id)

        # announce winner
        embed = embed_message(
            "We have a winner",
            f"Congratulation {winner.mention}!"
        )
        msg = await channel.send(embed=embed)

        # wait 10 mins and then delete
        await asyncio.sleep(60 * 10)
        await msg.delete()


    @cog_ext.cog_subcommand(
        base="tournament",
        base_description="Everything you need for in-house PvP tournaments",
        name="delete",
        description="Delete the tournament. Can only be used by the user who used '/tournament create' or an Admin",
    )
    async def _delete(self, ctx: SlashContext):
        # check if tourn exists
        message = await get_persistent_message(self.client, "tournament", ctx.guild.id)
        if not message:
            await ctx.send("Error: There is no tournament to delete", hidden=True)
            return

        # check if author has permissions to start
        if not (message.author == ctx.author) and not (await has_elevated_permissions(ctx.author, ctx.guild)):
            await ctx.send("Error: Only admins and the tournament creator can delete the tournament", hidden=True)
            return

        # delete msg
        await delete_persistent_message(message, "tournament", ctx.guild.id)

        await ctx.send(embed=embed_message(
            "Success",
            "The tournament has been deleted"
        ))


def setup(client):
    client.add_cog(DestinyCommands(client))
    client.add_cog(MysticCommands(client))
    client.add_cog(RankCommands(client))
    client.add_cog(WeaponCommands(client))
    client.add_cog(ClanActivitiesCommands(client))
    client.add_cog(TournamentCommands(client))
