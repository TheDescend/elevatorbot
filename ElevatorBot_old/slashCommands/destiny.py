import asyncio
import concurrent.futures
import datetime
import json
import os
from collections import Counter
from typing import Optional

import discord
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.utils import manage_components
from discord_slash.utils.manage_commands import create_option, create_choice
from pyvis.network import Network

from ElevatorBot.database.database import (
    getForges,
    getLastActivity,
    getDestinyDefinition,
    getWeaponInfo,
    getPgcrActivity,
    getTopWeapons,
    getActivityHistory,
    getPgcrActivitiesUsersStats,
    getClearCount,
    get_d2_steam_player_info,
    getTimePlayed,
)
from ElevatorBot.backendNetworking.authfunctions import getSpiderMaterials
from ElevatorBot.backendNetworking.dataLoading import (
    searchForItem,
    getClanMembers,
    translateWeaponSlot,
)
from ElevatorBot.backendNetworking.dataTransformation import getSeasonalChallengeInfo
from ElevatorBot.backendNetworking.destinyPlayer import DestinyPlayer
from ElevatorBot.backendNetworking.formating import embed_message
from ElevatorBot.backendNetworking.miscFunctions import (
    get_emoji,
    write_line,
    has_elevated_permissions,
    check_if_mutually_exclusive,
    convert_expansion_or_season_dates,
)
from ElevatorBot.backendNetworking.persistentMessages import (
    get_persistent_message_or_channel,
    make_persistent_message,
    delete_persistent_message,
)
from ElevatorBot.backendNetworking.slashCommandFunctions import (
    get_user_obj,
    get_user_obj_admin,
    verify_time_input,
)
from ElevatorBot.backendNetworking.tournament import startTournamentEvents
from ElevatorBot.networking.network import get_json_from_url
from ElevatorBot.static.config import CLANID
from ElevatorBot.static.dict import (
    raidHashes,
    gmHashes,
    expansion_dates,
    season_dates,
    zeroHashes,
    herzeroHashes,
    whisperHashes,
    herwhisperHashes,
    presageHashes,
    presageMasterHashes,
    prophHashes,
    pitHashes,
    throneHashes,
    harbHashes,
    requirementHashes,
)
from ElevatorBot.static.globals import (
    titan_emoji_id,
    hunter_emoji_id,
    warlock_emoji_id,
    light_level_icon_emoji_id,
    tournament,
    enter_emoji_id,
)
from ElevatorBot.static.slashCommandOptions import (
    choices_mode,
    options_stat,
    options_user,
)


class DestinyCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.classes = {
            "Warlock": warlock_emoji_id,
            "Hunter": hunter_emoji_id,
            "Titan": titan_emoji_id,
        }
        self.season_and_expansion_dates = sorted(expansion_dates + season_dates, key=lambda x: x[0])
        self.other_dates = [
            ["2019-10-04", "GoS"],
            ["2019-10-29", "PoH"],
            ["2020-01-14", "Corridors of Time"],
            ["2020-06-06", "Almighty Live Event"],
            ["2020-08-11", "Solstice of Heroes"],
            ["2020-11-21", "DSC"],
            ["2021-04-21", "Guardian Games"],
        ]
        self.other_dates_lower = [
            ["2020-02-04", "Empyrean Foundation"],
            ["2020-04-21", "Guardian Games"],
            ["2020-07-07", "Moments of Triumph"],
            ["2021-05-22", "VoG"],
        ]

    # @cog_ext.cog_slash(
    #     name="solos",
    #     description="Shows you an overview of your Destiny 2 solo activity completions",
    #     options=[options_user()],
    # )
    # async def _solos(self, ctx: SlashContext, **kwargs):
    #     user = await get_user_obj(ctx, kwargs)
    #     destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
    #     if not destiny_player:
    #         return
    #
    #     await ctx.defer()
    #
    #     interesting_solos = {
    #         "Shattered Throne": throneHashes,
    #         "Pit of Heresy": pitHashes,
    #         "Prophecy": prophHashes,
    #         "Harbinger": harbHashes,
    #         "Presage": presageHashes,
    #         "Master Presage": presageMasterHashes,
    #         "The Whisper": whisperHashes + herwhisperHashes,
    #         "Zero Hour": zeroHashes + herzeroHashes,
    #         "Grandmaster Nightfalls": gmHashes,
    #     }
    #
    #     # get the return text in a gather
    #     interesting_solos_texts = await asyncio.gather(
    #         *[
    #             self.get_formatted_solos_data(
    #                 destiny_player=destiny_player,
    #                 solo_activity_ids=solo_activity_ids,
    #             )
    #             for solo_activity_ids in interesting_solos.values()
    #         ]
    #     )
    #
    #     # start building the return embed
    #     embed = embed_message(f"{user.display_name}'s Destiny Solos")
    #
    #     # add the fields
    #     for solo_name, solo_activity_ids, solo_text in zip(
    #         interesting_solos.keys(),
    #         interesting_solos.values(),
    #         interesting_solos_texts,
    #     ):
    #         embed.add_field(
    #             name=solo_name,
    #             value=solo_text,
    #             inline=True,
    #         )
    #
    #     await ctx.send(embed=embed)

    # @staticmethod
    # async def get_formatted_solos_data(destiny_player: DestinyPlayer, solo_activity_ids: list[int]) -> str:
    #     """returns the formatted string to be used in self.solos()"""
    #
    #     results = await destiny_player.get_lowman_count(solo_activity_ids)
    #
    #     return (
    #         f"Solo Completions: **{results[0]}**\nSolo Flawless Count: **{results[1]}**\nFastest Solo: **{results[2]}**"
    #     )

    @cog_ext.cog_slash(
        name="time",
        description="Shows you your Destiny 2 playtime split up by season",
        options=[
            create_option(
                name="class",
                description="Default: 'Everything' - Which class you want to limit your playtime to",
                option_type=3,
                required=False,
                choices=[
                    create_choice(name="Everything", value="Everything"),
                    create_choice(name="Warlock", value="Warlock"),
                    create_choice(name="Hunter", value="Hunter"),
                    create_choice(name="Titan", value="Titan"),
                ],
            ),
            options_user(),
        ],
    )
    async def _time(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)
        destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
        if not destiny_player:
            return

        await ctx.defer()

        # init the db request function with all the args
        args = {
            "destinyID": destiny_player.destiny_id,
            "character_class": kwargs["class"] if ("class" in kwargs and kwargs["class"] != "Everything") else None,
        }

        # prepare embed for later use
        embed = embed_message(
            f"""{user.display_name} D2 Time Played {"- " + args["character_class"] if args["character_class"] else ""}""",
            f"**Total:** {str(datetime.timedelta(seconds=await getTimePlayed(**args)))} \n**PvE:** {str(datetime.timedelta(seconds=await getTimePlayed(**args, mode=7)))} \n**PvP:** {str(datetime.timedelta(seconds=await getTimePlayed(**args, mode=5)))}",
        )

        # init the dict where the results get saved
        results = {}

        # loop through the seasons
        for season in self.season_and_expansion_dates:
            season_date = datetime.datetime.strptime(season[0], "%Y-%m-%d")
            season_name = season[1]

            results[season_name] = {
                "Total": 0,
                "PvE": 0,
                "PvP": 0,
            }

            # get the next seasons start time as the cutoff or now if its the current season
            try:
                next_season_date = self.season_and_expansion_dates[(self.season_and_expansion_dates.index(season) + 1)][
                    0
                ]
                next_season_date = datetime.datetime.strptime(next_season_date, "%Y-%m-%d")
            except IndexError:
                next_season_date = datetime.datetime.now()

            args.update(
                {
                    "start_time": season_date,
                    "end_time": next_season_date,
                }
            )

            # loop through the modes
            for mode_name, mode in {"Total": None, "PvE": 7, "PvP": 5}.items():
                args.update({"mode": mode})

                # actually get time played now, using the definied args
                time_played = await getTimePlayed(**args)
                results[season_name].update({mode_name: time_played})

        # loop through the results and add embed fields
        for season_name, season_values in results.items():
            # only append season info if they actually played that season
            if season_values["Total"] == 0:
                continue

            text = []
            for activity, value in season_values.items():
                text.append(f"**{activity}**: {str(datetime.timedelta(seconds=value))}")
            embed.add_field(name=season_name, value="\n".join(text), inline=True)

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="poptimeline",
        description="Shows the Destiny 2 steam population timeline",
    )
    async def _poptimeline(self, ctx: SlashContext):
        # reading data from the DB
        data = await get_d2_steam_player_info()

        # Create figure and plot space
        fig, ax = plt.subplots(figsize=(20, 10))
        ax.yaxis.grid(True)

        # filling plot
        ax.plot(data["dateobj"], data["numberofplayers"], "darkred", zorder=2)

        # Set title and labels for axes
        ax.set_xlabel("Date", fontsize=20, fontweight="bold")
        ax.set_ylabel("Players", fontsize=20, fontweight="bold")

        # adding nice lines to mark important events
        for dates in self.season_and_expansion_dates[7:]:
            date = datetime.datetime.strptime(dates[0], "%Y-%m-%d")
            ax.axvline(date, color="darkgreen", zorder=1)
            ax.text(
                date + datetime.timedelta(days=2),
                (max(data["numberofplayers"]) - min(data["numberofplayers"])) * 1.02 + min(data["numberofplayers"]),
                dates[1],
                color="darkgreen",
                fontweight="bold",
                bbox=dict(facecolor="white", edgecolor="darkgreen", pad=4, zorder=3),
            )
        for dates in self.other_dates:
            date = datetime.datetime.strptime(dates[0], "%Y-%m-%d")
            ax.axvline(date, color="mediumaquamarine", zorder=1)
            ax.text(
                date + datetime.timedelta(days=2),
                (max(data["numberofplayers"]) - min(data["numberofplayers"])) * 0.95 + min(data["numberofplayers"]),
                dates[1],
                color="mediumaquamarine",
                bbox=dict(
                    facecolor="white",
                    edgecolor="mediumaquamarine",
                    boxstyle="round",
                    zorder=3,
                ),
            )
        for dates in self.other_dates_lower:
            date = datetime.datetime.strptime(dates[0], "%Y-%m-%d")
            ax.axvline(date, color="mediumaquamarine", zorder=1)
            ax.text(
                date + datetime.timedelta(days=2),
                (max(data["numberofplayers"]) - min(data["numberofplayers"])) * 0.90 + min(data["numberofplayers"]),
                dates[1],
                color="mediumaquamarine",
                bbox=dict(
                    facecolor="white",
                    edgecolor="mediumaquamarine",
                    boxstyle="round",
                    zorder=3,
                ),
            )

        # saving file
        title = "d2population.png"
        plt.savefig(title, bbox_inches="tight")

        # sending them the file
        embed = embed_message("Destiny 2 - Steam Player Count")
        image = discord.File(title)
        embed.set_image(url=f"attachment://{title}")
        await ctx.send(file=image, embed=embed)

        # _delete file
        await asyncio.sleep(10)
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
                choices=choices_mode,
            ),
            options_user(),
        ],
    )
    async def _last(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)
        destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
        if not destiny_player:
            return

        # might take a sec
        await ctx.defer()

        # get data for the mode specified
        await destiny_player.update_activity_db()
        data = await getLastActivity(
            destiny_player.destiny_id,
            mode=int(kwargs["activity"]) if "activity" in kwargs and kwargs["activity"] != "0" else None,
        )
        if not data:
            await ctx.send(
                embed=embed_message(
                    "Error",
                    "Couldn't find any data for that mode. If you think this is an error DM me",
                )
            )
            return

        # make data pretty and send msg
        activity_name = (await getDestinyDefinition("DestinyActivityDefinition", data["directorActivityHash"]))[2]
        embed = embed_message(
            f"{user.display_name}'s Last Activity",
            f"**{activity_name}{(' - ' + str(data['score']) + ' Points') if data['score'] > 0 else ''} - {str(datetime.timedelta(seconds=data['activityDurationSeconds']))}**",
            f"Date: {data['period'].strftime('%d/%m/%Y, %H:%M')} - InstanceID: {data['instanceID']}",
        )

        for player in data["entries"]:
            player_data = [
                f"K: **{player['opponentsDefeated']}**, D: **{player['deaths']}**, A: **{player['assists']}**",
                f"K/D: **{round((player['opponentsDefeated'] / player['deaths']) if player['deaths'] > 0 else player['opponentsDefeated'], 2)}** {'(DNF)' if not player['completed'] else ''}",
                str(datetime.timedelta(seconds=player["timePlayedSeconds"])),
            ]

            # sometimes people dont have a class for some reason. Skipping that
            if player["characterClass"] == "":
                continue
            embed.add_field(
                name=f"{await get_emoji(self.client, self.classes[player['characterClass']])} {(await destiny_player.get_destiny_name_and_last_played())[0]} {await get_emoji(self.client, light_level_icon_emoji_id)} {player['lightLevel']}",
                value="\n".join(player_data),
                inline=True,
            )

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="challenges",
        description="Shows you the seasonal challenges and your completion status",
        options=[options_user()],
    )
    async def _challenges(self, ctx: SlashContext, **kwargs):
        await ctx.defer()
        user = await get_user_obj(ctx, kwargs)
        destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
        if not destiny_player:
            return

        # get seasonal challenge info
        seasonal_challenges = await getSeasonalChallengeInfo()
        start = list(seasonal_challenges)[0]

        # get player triumphs
        user_triumphs = await destiny_player.get_triumphs()

        # get select components
        components = [
            manage_components.create_actionrow(
                manage_components.create_select(
                    options=[
                        manage_components.create_select_option(
                            emoji="📅",
                            label=week,
                            value=week,
                        )
                        for week in seasonal_challenges
                    ],
                    placeholder="Select the week you want to see",
                    min_values=1,
                    max_values=1,
                )
            ),
        ]

        # send data and wait for new user input
        await self._send_challenge_info(
            ctx.author,
            user,
            start,
            seasonal_challenges,
            user_triumphs,
            components,
            ctx=ctx,
        )

    async def _send_challenge_info(
        self,
        author: discord.Member,
        user: discord.Member,
        week: str,
        seasonal_challenges: dict,
        user_triumphs: dict,
        select_components: list,
        ctx: SlashContext = None,
        select_ctx: ComponentContext = None,
        message: discord.Message = None,
    ) -> None:
        # this is a recursive commmand.

        # make data pretty
        embed = await self._get_challenge_info(user, week, seasonal_challenges, user_triumphs)

        # send message
        if not select_ctx:
            message = await ctx.send(embed=embed, components=select_components)
        else:
            await select_ctx.edit_origin(embed=embed)

        # wait 60s for selection
        def check(select_ctx: ComponentContext):
            return select_ctx.author == author

        try:
            select_ctx: ComponentContext = await manage_components.wait_for_component(
                select_ctx.bot if select_ctx else ctx.bot,
                components=select_components,
                timeout=60,
            )
        except asyncio.TimeoutError:
            await message.edit(components=None)
            return
        else:
            new_week = select_ctx.selected_options[0]

            # recursively call this function
            await self._send_challenge_info(
                author,
                user,
                new_week,
                seasonal_challenges,
                user_triumphs,
                select_components,
                select_ctx=select_ctx,
                message=message,
            )

    @staticmethod
    async def _get_challenge_info(
        user: discord.Member, week: str, seasonal_challenges: dict, user_triumphs: dict
    ) -> discord.Embed:
        """Returns an embed for the specified week"""
        embed = embed_message(f"{user.display_name}'s Seasonal Challenges - {week}")

        # add the triumphs and what the user has done
        for triumph in seasonal_challenges[week]:
            user_triumph = user_triumphs[str(triumph["referenceID"])]

            # calculate completion rate
            rate = []
            for objective in user_triumph["objectives"]:
                rate.append(objective["progress"] / objective["completionValue"] if not objective["complete"] else 1)
            rate = sum(rate) / len(rate)

            # make emoji art for completion rate
            bar_length = 10
            bar_text = ""
            for i in range(bar_length):
                if round(rate, 1) <= 1 / bar_length * i:
                    bar_text += "░"
                else:
                    bar_text += "▓"

            # add field to embed
            embed.add_field(
                name=f"""{triumph["name"]}   |   {bar_text}  {int(rate * 100)}%""",
                value=triumph["description"],
                inline=False,
            )

        return embed

    # todo not really needed
    @cog_ext.cog_slash(
        name="spoder",
        description="The better /spider command to show Spiders current inventory",
        options=[options_user()],
    )
    async def _spoder(self, ctx: SlashContext, **kwargs):
        await ctx.defer()
        user = await get_user_obj_admin(ctx, kwargs)
        if not user:
            return
        destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
        if not destiny_player:
            return
        anyCharID = list(await destiny_player.get_character_info())[0]

        # get and send spider inv
        materialtext = await getSpiderMaterials(destiny_player.discord_id, destiny_player.destiny_id, anyCharID)
        if "embed" in materialtext:
            await ctx.send(embed=materialtext["embed"])
        elif materialtext["result"]:
            await ctx.send(materialtext["result"])
        else:
            await ctx.send(materialtext["error"])

    # @cog_ext.cog_slash(
    #     name="destiny",
    #     description="Gives you various destiny stats",
    #     options=[options_user()],
    # )
    # async def _destiny(self, ctx: SlashContext, **kwargs):
    #     await ctx.defer()
    #
    #     # get basic user data
    #     user = await get_user_obj(ctx, kwargs)
    #     destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
    #     if not destiny_player:
    #         return
    #
    #     heatmap_url = f"https://chrisfried.github.io/secret-scrublandeux/guardian/{destiny_player.system}/{destiny_player.destiny_id}"
    #
    #     # get character infos
    #     characters = await destiny_player.get_character_info()
    #
    #     character_playtime = {}  # in seconds
    #     for characterID in characters:
    #         character_playtime[characterID] = await destiny_player.get_stat_value(
    #             "secondsPlayed", character_id=characterID
    #         )
    #
    #     embed = embed_message(
    #         f"{user.display_name}'s Destiny Stats",
    #         f"**Total Playtime:** {str(datetime.timedelta(seconds=sum(character_playtime.values())))} \n[Click to see your heatmap]({heatmap_url})",
    #         "For info on achievable discord roles, type !roles",
    #     )
    #
    #     """ char info field """
    #     embed.add_field(name="⁣", value=f"__**Characters:**__", inline=False)
    #     for characterID in characters:
    #         text = f"""Playtime: {str(datetime.timedelta(seconds=character_playtime[characterID]))} \n⁣\nPower: {await destiny_player.get_stat_value("highestLightLevel", character_id=characterID):,} \nActivities: {await destiny_player.get_stat_value("activitiesCleared", character_id=characterID):,} \nKills: {await destiny_player.get_stat_value("kills", character_id=characterID):,} \nDeaths: {await destiny_player.get_stat_value("deaths", character_id=characterID):,} \nEfficiency: {round(await destiny_player.get_stat_value("efficiency", character_id=characterID), 2)}"""
    #         embed.add_field(
    #             name=f"""{characters[characterID]["class"]} ({characters[characterID]["race"]} / {characters[characterID]["gender"]})""",
    #             value=text,
    #             inline=True,
    #         )
    #
    #     """ triumph info field """
    #     embed.add_field(name="⁣", value=f"__**Triumphs:**__", inline=False)
    #
    #     # get triumph data
    #     triumphs = await destiny_player.get_triumphs()
    #     embed.add_field(
    #         name="Lifetime Triumph Score",
    #         value=f"""{triumphs["profileRecords"]["data"]["lifetimeScore"]:,}""",
    #         inline=True,
    #     )
    #     embed.add_field(
    #         name="Active Triumph Score",
    #         value=f"""{triumphs["profileRecords"]["data"]["activeScore"]:,}""",
    #         inline=True,
    #     )
    #     embed.add_field(
    #         name="Legacy Triumph Score",
    #         value=f"""{triumphs["profileRecords"]["data"]["legacyScore"]:,}""",
    #         inline=True,
    #     )
    #
    #     # get triumph completion rate
    #     triumphs_data = triumphs["profileRecords"]["data"]["records"]
    #     triumphs_completed = 0
    #     triumphs_no_data = 0
    #     for triumph in triumphs_data.values():
    #         status = True
    #         if "objectives" in triumph:
    #             for part in triumph["objectives"]:
    #                 status &= part["complete"]
    #         elif "intervalObjectives" in triumph:
    #             for part in triumph["intervalObjectives"]:
    #                 status &= part["complete"]
    #         else:
    #             triumphs_no_data += 1
    #             continue
    #         if status:
    #             triumphs_completed += 1
    #     embed.add_field(
    #         name="Triumphs",
    #         value=f"{triumphs_completed} / {len(triumphs_data) - triumphs_no_data}",
    #         inline=True,
    #     )
    #
    #     # get seal completion rate
    #     total_seals, completed_seals = await destiny_player.get_player_seals()
    #     embed.add_field(
    #         name="Seals",
    #         value=f"{len(completed_seals)} / {len(total_seals)}",
    #         inline=True,
    #     )
    #
    #     await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="stat",
        base_description="Shows you various Destiny 2 stats",
        name="everything",
        description="Displays information for all activities",
        options=[options_stat, options_user()],
    )
    async def _stat_everything(self, ctx: SlashContext, **kwargs):
        # get basic user data
        user = await get_user_obj(ctx, kwargs)
        destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
        if not destiny_player:
            return

        # might take a sec
        await ctx.defer()

        # get stat
        stat = await destiny_player.get_stat_value(kwargs["name"])
        await ctx.send(
            embed=embed_message(
                f"{user.display_name}'s Stat Info",
                f"Your `{kwargs['name']}` stat is currently at **{stat:,}**",
            )
        )

    @cog_ext.cog_subcommand(
        base="stat",
        base_description="Shows you various Destiny 2 stats",
        name="pve",
        description="Displays information for all PvE activities",
        options=[options_stat, options_user()],
    )
    async def _stat_pve(self, ctx: SlashContext, **kwargs):
        # get basic user data
        user = await get_user_obj(ctx, kwargs)
        destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
        if not destiny_player:
            return

        # might take a sec
        await ctx.defer()

        # get stat
        stat = await destiny_player.get_stat_value(kwargs["name"], stat_category="allPvE")
        await ctx.send(
            embed=embed_message(
                f"{user.display_name}'s PvE Stat Info",
                f"Your `{kwargs['name']}` stat is currently at **{stat:,}**",
            )
        )

    @cog_ext.cog_subcommand(
        base="stat",
        base_description="Shows you various Destiny 2 stats",
        name="pvp",
        description="Displays information for all PvP activities",
        options=[options_stat, options_user()],
    )
    async def _stat_pvp(self, ctx: SlashContext, **kwargs):
        # get basic user data
        user = await get_user_obj(ctx, kwargs)
        destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
        if not destiny_player:
            return

        # might take a sec
        await ctx.defer()

        # get stat
        stat = await destiny_player.get_stat_value(kwargs["name"], stat_category="allPvP")
        await ctx.send(
            embed=embed_message(
                f"{user.display_name}'s PvP Stat Info",
                f"Your `{kwargs['name']}` stat is currently at **{stat:,}**",
            )
        )


class ClanActivitiesCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="clanactivity",
        description="Shows information about who from the clan plays with whom (Default: in the last 7 days)",
        options=[
            create_option(
                name="mode",
                description="You can restrict the game mode",
                option_type=3,
                required=False,
                choices=choices_mode,
            ),
            create_option(
                name="starttime",
                description="Format: 'DD/MM/YY' - You can restrict the start (lower cutoff). Note: Can break for long timespan",
                option_type=3,
                required=False,
            ),
            create_option(
                name="endtime",
                description="Format: 'DD/MM/YY' - You can restrict the end  (higher cutoff)",
                option_type=3,
                required=False,
            ),
            options_user(flavor_text="The name of the user you want to highlight"),
        ],
    )
    async def _clanactivity(self, ctx: SlashContext, **kwargs):
        # edge_list = [person, size, size_desc, display_names, colors]
        self.edge_list = []
        self.ignore = []

        user = await get_user_obj(ctx, kwargs)
        destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
        if not destiny_player:
            return

        # get params
        mode = int(kwargs["mode"]) if "mode" in kwargs else None
        start_time = (
            await verify_time_input(ctx, kwargs["starttime"])
            if "starttime" in kwargs
            else datetime.datetime.now() - datetime.timedelta(days=7)
        )
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

        result = await asyncio.gather(
            *[
                self._handle_members(destinyID, mode, start_time, end_time, user.display_name)
                for destinyID in self.clan_members
            ]
        )
        for res in result:
            if res is not None:
                destinyID = res[0]

                self.activities_from_user_who_got_looked_at[destinyID] = res[1]
                self.friends[destinyID] = res[2]

        data_temp = []
        for destinyID in self.friends:
            for friend in self.friends[destinyID]:
                # data = [destinyID1, destinyID2, number of activities together]
                data_temp.append(
                    [
                        int(str(destinyID)[-9:]),
                        int(str(friend)[-9:]),
                        self.friends[destinyID][friend],
                    ]
                )

        data = np.array(data_temp)
        del data_temp

        # getting the display names, colors for users in discord, size of blob
        await asyncio.gather(
            *[
                self._prep_data(
                    await DestinyPlayer.from_destiny_id(destinyID),
                    destiny_player.destiny_id,
                )
                for destinyID in self.clan_members
            ]
        )

        # building the network graph
        net = Network()

        # adding nodes
        # edge_list = [person, size, size_desc, display_names, colors]
        for edge_data in self.edge_list:
            net.add_node(
                int(str(edge_data[0])[-9:]),
                value=edge_data[1],
                title=edge_data[2],
                label=edge_data[3],
                color=edge_data[4],
            )

        # adding edges with data = [user1, user2, number of activities together]
        with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 5) as pool:
            futurelist = [pool.submit(self._add_edge, net, edge) for edge in data]
            for _ in concurrent.futures.as_completed(futurelist):
                pass

        net.barnes_hut(
            gravity=-200000,
            central_gravity=0.3,
            spring_length=200,
            spring_strength=0.005,
            damping=0.09,
            overlap=0,
        )
        net.show_buttons(filter_=["physics"])

        # saving the file
        title = user.display_name + ".html"
        net.save_graph(title)

        # letting user know it's done
        await ctx.send(
            embed=embed_message(
                f"{user.display_name}'s Friends",
                f"Click the download button below and open the file with your browser to view your Network",
                f"The file may load for a while, that's normal.",
            )
        )
        # sending them the file
        await ctx.channel.send(file=discord.File(title))

        # _delete file
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

    async def _prep_data(self, destiny_player: DestinyPlayer, orginal_user_destiny_id):
        display_name, _ = await destiny_player.get_destiny_name_and_last_played()

        size = self.activities_from_user_who_got_looked_at[destiny_player.destiny_id] * 50
        size_desc = str(self.activities_from_user_who_got_looked_at[destiny_player.destiny_id]) + " Activities"

        colors = "#850404" if orginal_user_destiny_id == destiny_player.destiny_id else "#006aff"

        # edge_list = [person, size, size_desc, display_names, colors]
        self.edge_list.append([destiny_player.destiny_id, size, size_desc, display_name, colors])

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
        return "\n".join(
            map(
                lambda p: c.name if (c := self.client.get_user(p["id"])) else "InvalidUser",
                userdict,
            )
        )

    # todo not needed
    @cog_ext.cog_subcommand(
        base="mystic",
        base_description="Everything concerning Mystic's abandoned carry list. Tbf he said he tried ¯\_(ツ)_/¯",
        name="list",
        description="Displays the current list",
    )
    async def _list(self, ctx: SlashContext):
        with open("database/mysticlist.json", "r+") as mlist:
            players = json.load(mlist)

        embed = embed_message("Mystic List", f"The following users are currently in the list:")
        embed.add_field(name="Users", value=self.names(players), inline=True)

        await ctx.send(embed=embed)

    # todo not needed
    @cog_ext.cog_subcommand(
        base="mystic",
        base_description="Everything concerning Mystic's abandoned carry list. Tbf he said he tried ¯\_(ツ)_/¯",
        name="add",
        description="Add a user to the list",
        options=[options_user(flavor_text="Requires elevated permissions")],
    )
    async def _add(self, ctx: SlashContext, **kwargs):
        # allow mystic himself
        user = await get_user_obj_admin(ctx, kwargs, allowed_users=[211838266834550785])
        if not user:
            return

        with open("database/mysticlist.json", "r") as mlist:
            players = json.load(mlist)

        # add new player
        players.append({"name": user.display_name, "id": user.id})

        with open("commands/mysticlog.log", "a") as mlog:
            mlog.write(f"\n{ctx.author.name} added {user.name}")

        with open("database/mysticlist.json", "w") as mlist:
            json.dump(players, mlist)

        embed = embed_message("Mystic List", f"Added {user.name} to the mystic list, it now has:")
        embed.add_field(name="Users", value=self.names(players), inline=True)

        await ctx.send(embed=embed)

    # todo not needed
    @cog_ext.cog_subcommand(
        base="mystic",
        base_description="Everything concerning Mystic's abandoned carry list. Tbf he said he tried ¯\_(ツ)_/¯",
        name="_delete",
        description="Remove a user from the list",
        options=[options_user(flavor_text="Requires elevated permissions")],
    )
    async def _remove(self, ctx: SlashContext, **kwargs):
        # allow mystic himself
        user = await get_user_obj_admin(ctx, kwargs, allowed_users=[211838266834550785])
        if not user:
            return

        with open("database/mysticlist.json", "r") as mlist:
            players = json.load(mlist)

        if len(player := list(filter(lambda muser: muser["id"] == user.id, players))) == 1:
            # _delete player
            players._delete(player[0])
            with open("commands/mysticlog.log", "a") as mlog:
                mlog.write(f"\n{ctx.author.name} removed {user.name}")

            with open("database/mysticlist.json", "w+") as mlist:
                json.dump(players, mlist)

            embed = embed_message("Mystic List", f"Removed {user.name} from the mystic list, it now has:")
            embed.add_field(name="Users", value=self.names(players), inline=True)

            await ctx.send(embed=embed)
            return

        await ctx.send(embed=embed_message("Mystic List", f"User {user.name} was not found in the player list"))


class RankCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.stats = {
            "mobility": 2996146975,
            "resilience": 392767087,
            "recovery": 1943323491,
            "discipline": 1735777505,
            "intellect": 144602215,
            "strength": 4244567218,
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
                    create_choice(name="Join-Date of this Discord Server", value="discordjoindate"),
                    create_choice(name="Roles Earned on this Discord Server", value="roles"),
                    create_choice(name="Total Playtime", value="totaltime"),
                    create_choice(name="Max. Power Level", value="maxpower"),
                    create_choice(name="Vault Space Used", value="vaultspace"),
                    create_choice(name="Orbs of Power Generated", value="orbs"),
                    create_choice(name="Melee Kills", value="meleekills"),
                    create_choice(name="Super Kills", value="superkills"),
                    create_choice(name="Grenade Kills", value="grenadekills"),
                    create_choice(name="Deaths", value="deaths"),
                    create_choice(name="Suicides", value="suicides"),
                    create_choice(name="Kills", value="kills"),
                    create_choice(name="Raids Done", value="raids"),
                    create_choice(name="Raid Time", value="raidtime"),
                    create_choice(name="Grandmaster Nightfalls Done", value="gm"),
                    create_choice(name="Weapon Kills", value="weapon"),
                    create_choice(name="Weapon Precision Kills", value="weaponprecision"),
                    create_choice(name="% Weapon Precision Kills", value="weaponprecisionpercent"),
                    create_choice(name="Enhancement Cores", value="enhancementcores"),
                    create_choice(name="Forges Done", value="forges"),
                    # create_choice(
                    #     name="AFK Forges Done",
                    #     value="afkforges"
                    # ),
                    create_choice(name="Active Triumph Score", value="activetriumphs"),
                    create_choice(name="Legacy Triumph Score", value="legacytriumphs"),
                    create_choice(name="Triumph Score", value="triumphs"),
                    # create_choice(
                    #     name="Laurels collected",
                    #     value="laurels"
                    # ),
                ],
            ),
            create_option(
                name="arg",
                description="Depending on which leaderboard you want to see, you might need to add an additional argument",
                option_type=3,
                required=False,
            ),
            create_option(
                name="reverse",
                description="Default: 'False' - If you want to flip the sorting",
                option_type=5,
                required=False,
            ),
            options_user(),
        ],
    )
    async def _rank(self, ctx: SlashContext, *args, **kwargs):
        if not ctx.deferred:
            await ctx.defer()

        if args:
            print(f"Got unexpected args: {args}")

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
                await ctx.send(
                    hidden=True,
                    embed=embed_message(
                        f"Error",
                        f"Please specify a weapon in the command argument `arg`",
                    ),
                )
                return

        # calculate the leaderboard
        if embed := (
            await self._handle_users(
                leaderboard,
                user.display_name,
                ctx.guild,
                item_hashes,
                item_name,
                reverse=kwargs["reverse"] if "reverse" in kwargs else False,
            )
        ):
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed_message("Error", "Failed handling users"))

    async def _handle_users(self, stat, display_name, guild, extra_hash, extra_name, reverse=False):
        # init DF. "stat_sort" is only here, since I want to save numbers fancy (1,000,000) and that is a string and not an int so sorting wont work
        data = pd.DataFrame(columns=["member", "stat", "stat_sort"])

        # loop through the clan members
        clan_members = (await get_json_from_url(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/")).content[
            "Response"
        ]["results"]
        results = await asyncio.gather(
            *[self._handle_user(stat, member, guild, extra_hash, extra_name) for member in clan_members]
        )
        if len(results) < 1:
            return embed_message("Error", "No users found")
        sort_by_ascending = None
        for ret in results:
            # add user to DF
            if ret:
                data = data.append(
                    {"member": ret[0], "stat": ret[1], "stat_sort": ret[2]},
                    ignore_index=True,
                )

                # the flavor text of the leaderboard, fe "Top Clanmembers by D2 Total Time Logged In" for totaltime
                leaderboard_text = ret[3]
                # the flavor text the stat will have, fe. "hours" for totaltime
                stat_text = ret[4]
                # for some stats lower might be better
                sort_by_ascending = ret[5]

        if data.empty:
            return embed_message("Error", "No data found")

        if reverse:
            sort_by_ascending = not sort_by_ascending

        # sort and prepare DF
        data.sort_values(by=["stat_sort"], inplace=True, ascending=sort_by_ascending)
        data.reset_index(drop=True, inplace=True)

        # calculate the data for the embed
        ranking = []
        emoji = self.client.get_emoji(enter_emoji_id)
        found = False
        for index, row in data.iterrows():
            if len(ranking) < 12:
                # setting a flag if user is in list
                if row["member"] == display_name:
                    found = True
                    ranking.append(
                        write_line(
                            index + 1,
                            f"""**{row["member"]}**""",
                            stat_text,
                            row["stat"],
                            emoji,
                        )
                    )
                else:
                    ranking.append(write_line(index + 1, row["member"], stat_text, row["stat"], emoji))

            # looping through rest until original user is found
            elif (len(ranking) >= 12) and (not found):
                # adding only this user
                if row["member"] == display_name:
                    ranking.append("...")
                    ranking.append(write_line(index + 1, row["member"], stat_text, row["stat"], emoji))
                    break

            else:
                break

        # make and return embed
        return embed_message(leaderboard_text, "\n".join(ranking))

    async def _handle_user(self, stat, member, guild, extra_hash, extra_name):
        destiny_player = await DestinyPlayer.from_destiny_id(int(member["destinyUserInfo"]["membershipId"]))

        if not (destiny_player and await destiny_player.has_token()):
            return None

        sort_by_ascending = False

        # catch people that are in the clan but not in discord, shouldn't happen tho
        discord_member = destiny_player.get_discord_member(guild)
        if not discord_member:
            return None
        name = discord_member.display_name

        # get the stat that we are looking for
        if stat == "discordjoindate":
            sort_by_ascending = True
            leaderboard_text = "Top Clanmembers by Discord Join Date"
            stat_text = "Date"

            result_sort = discord_member.joined_at
            result = discord_member.joined_at.strftime("%d/%m/%Y, %H:%M")

        elif stat == "roles":
            sort_by_ascending = True
            leaderboard_text = "Top Clanmembers by Discord Roles Earned"
            stat_text = "Roles missing"

            earned_roles = [role.name for role in discord_member.roles]
            missing_roles = []
            missing_roles_legacy = []

            # loop through the dict
            for topic in requirementHashes:
                for role in requirementHashes[topic]:
                    # check if user has the role / a superior one
                    if role not in earned_roles:
                        replaced_by_role_earned = False
                        if "replaced_by" in requirementHashes[topic][role]:
                            for replaced_role in requirementHashes[topic][role]["replaced_by"]:
                                if replaced_role in earned_roles:
                                    replaced_by_role_earned = True

                        if not replaced_by_role_earned:
                            if "deprecated" not in requirementHashes[topic][role]:
                                missing_roles.append(role)
                            else:
                                missing_roles_legacy.append(role)

            result_sort = len(set(missing_roles))
            result = f"{result_sort:,} ({len(set(missing_roles_legacy)):,} Legacy Roles)"

        elif stat == "totaltime":
            leaderboard_text = "Top Clanmembers by D2 Total Time Logged In"
            stat_text = "Total"

            # in hours
            result_sort = await destiny_player.get_stat_value("secondsPlayed")
            result = str(datetime.timedelta(seconds=result_sort))

        elif stat == "orbs":
            leaderboard_text = "Top Clanmembers by PvE Orbs Generated"
            stat_text = "Orbs"

            result_sort = await destiny_player.get_stat_value("orbsDropped", stat_category="pve")
            result = f"{result_sort:,}"

        elif stat == "meleekills":
            leaderboard_text = "Top Clanmembers by D2 PvE Meleekills"
            stat_text = "Kills"

            result_sort = await destiny_player.get_stat_value("weaponKillsMelee", stat_category="pve")
            result = f"{result_sort:,}"

        elif stat == "superkills":
            leaderboard_text = "Top Clanmembers by D2 PvE Superkills"
            stat_text = "Kills"

            result_sort = await destiny_player.get_stat_value("weaponKillsSuper", stat_category="pve")
            result = f"{result_sort:,}"

        elif stat == "grenadekills":
            leaderboard_text = "Top Clanmembers by D2 PvE Grenadekills"
            stat_text = "Kills"

            result_sort = await destiny_player.get_stat_value("weaponKillsGrenade", stat_category="pve")
            result = f"{result_sort:,}"

        elif stat == "deaths":
            leaderboard_text = "Top Clanmembers by D2 PvE Deaths"
            stat_text = "Deaths"

            result_sort = await destiny_player.get_stat_value("deaths", stat_category="pve")
            result = f"{result_sort:,}"

        elif stat == "suicides":
            leaderboard_text = "Top Clanmembers by D2 PvE Suicides"
            stat_text = "Suicides"

            result_sort = await destiny_player.get_stat_value("suicides", stat_category="pve")
            result = f"{result_sort:,}"

        elif stat == "kills":
            leaderboard_text = "Top Clanmembers by D2 PvE Kills"
            stat_text = "Kills"

            result_sort = await destiny_player.get_stat_value("suicides", stat_category="pve")
            result = f"{result_sort:,}"

        elif stat == "maxpower":
            # # TODO efficiency
            # leaderboard_text = "Top Clanmembers by D2 Maximum Reported Power"
            # stat_text = "Power"
            #
            # artifact_power = (await destiny_player.get_artifact())["powerBonus"]
            #
            # items = await getCharacterGearAndPower(destiny_player.destiny_id)
            # items = self._sort_gear_by_slot(items)
            #
            # results = await asyncio.gather(*[self._get_highest_item_light_level(slot) for slot in items])
            #
            # total_power = 0
            # for ret in results:
            #     total_power += ret
            # total_power /= 8
            #
            # result_sort = int(total_power + artifact_power)
            # result = f"{int(total_power):,} + {artifact_power:,}"

            # temporay result
            result_sort = 0
            result = "0"

        elif stat == "vaultspace":
            sort_by_ascending = True

            leaderboard_text = "Top Clanmembers by D2 Vaultspace Used"
            stat_text = "Used Space"

            result_sort = len(await destiny_player.get_inventory_bucket())
            result = f"{result_sort:,}"

        elif stat == "raids":
            leaderboard_text = "Top Clanmembers by D2 Total Raid Completions"
            stat_text = "Total"

            result_sort = await getClearCount(destiny_player.destiny_id, mode=4)
            result = f"{result_sort:,}"

        elif stat == "raidtime":
            leaderboard_text = "Top Clanmembers by D2 Total Raid Time"
            stat_text = "Hours"

            # in hours
            result_sort = int(
                (await self._add_activity_stats(destiny_player, raidHashes, "activitySecondsPlayed")) / 60 / 60
            )
            result = f"{result_sort:,}"

        elif stat == "forges":
            leaderboard_text = "Top Clanmembers by D2 Forge Completions"
            stat_text = "Total"

            result_sort = 0
            farmed_runs = 0
            for _, kills in await getForges(destiny_player.destiny_id):
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
            for _, kills in await getForges(destiny_player.destiny_id):
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
            items = await destiny_player.get_inventory_bucket()
            for item in items:
                if item["itemHash"] == 3853748946:
                    result_sort += item["quantity"]

            items = await destiny_player.get_inventory_bucket(bucket=1469714392)
            for item in items:
                if item["itemHash"] == 3853748946:
                    result_sort += item["quantity"]
            result = f"{result_sort:,}"

        elif stat == "weapon":
            leaderboard_text = f"Top Clanmembers by {extra_name} Kills"
            stat_text = "Kills"

            result_sort, _ = await destiny_player.get_weapon_stats(extra_hash)
            result = f"{result_sort:,}"

        elif stat == "weaponprecision":
            leaderboard_text = f"Top Clanmembers by {extra_name} Precision Kills"
            stat_text = "Kills"

            _, result_sort = await destiny_player.get_weapon_stats(extra_hash)
            result = f"{result_sort:,}"

        elif stat == "weaponprecisionpercent":
            leaderboard_text = f"Top Clanmembers by {extra_name} % Precision Kills"
            stat_text = "Kills"

            kills, prec_kills = await destiny_player.get_weapon_stats(extra_hash)
            result_sort = prec_kills / kills if kills != 0 else 0
            result = f"{round(result_sort * 100, 2)}%"

        elif stat == "activetriumphs":
            leaderboard_text = f"Top Clanmembers by D2 Active Triumph Score"
            stat_text = "Score"

            result_sort = (await destiny_player.get_triumphs())["profileRecords"]["data"]["activeScore"]
            result = f"{result_sort:,}"

        elif stat == "legacytriumphs":
            leaderboard_text = f"Top Clanmembers by D2 Legacy Triumph Score"
            stat_text = "Score"

            result_sort = (await destiny_player.get_triumphs())["profileRecords"]["data"]["legacyScore"]
            result = f"{result_sort:,}"

        elif stat == "triumphs":
            leaderboard_text = f"Top Clanmembers by D2 Lifetime Triumph Score"
            stat_text = "Score"

            result_sort = (await destiny_player.get_triumphs())["profileRecords"]["data"]["lifetimeScore"]
            result = f"{result_sort:,}"

        elif stat == "gm":
            leaderboard_text = f"Top Clanmembers by D2 Grandmaster Nightfall Completions"
            stat_text = "Total"

            result_sort = await getClearCount(destiny_player.destiny_id, activityHashes=gmHashes)
            result = f"{result_sort:,}"

        elif stat == "laurels":
            leaderboard_text = f"Top Clanmembers by Laurels collected in S13"
            stat_text = "Count"

            result_sort = await destiny_player.get_metric_value("473272243")
            if not result_sort:
                result_sort = 0
            result = f"{result_sort:,}"

        else:
            return

        return [
            name,
            result,
            result_sort,
            leaderboard_text,
            stat_text,
            sort_by_ascending,
        ]

    async def _add_activity_stats(self, destiny_player: DestinyPlayer, hashes, stat):
        result_sort = 0
        chars = await destiny_player.get_character_info()
        for characterID in chars:
            aggregateStats = await destiny_player.get_character_activity_stats(characterID)

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
            if item["lightlevel"] > max_power:
                max_power = item["lightlevel"]
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

    # todo _delete
    def _add_stats(self, stat_json, stat, scope="all"):
        result_sort = 0
        if scope == "all":
            result_sort = int(stat_json["mergedAllCharacters"]["merged"]["allTime"][stat]["basic"]["value"])
            try:
                result_sort += int(stat_json["mergedDeletedCharacters"]["merged"]["allTime"][stat]["basic"]["value"])
            except:
                pass
        elif scope == "pve":
            result_sort = int(stat_json["mergedAllCharacters"]["results"]["allPvE"]["allTime"][stat]["basic"]["value"])
            try:
                result_sort += int(
                    stat_json["mergedDeletedCharacters"]["results"]["allPvE"]["allTime"][stat]["basic"]["value"]
                )
            except:
                pass
        elif scope == "pvp":
            result_sort = int(stat_json["mergedAllCharacters"]["results"]["allPvP"]["allTime"][stat]["basic"]["value"])
            try:
                result_sort += int(
                    stat_json["mergedDeletedCharacters"]["results"]["allPvP"]["allTime"][stat]["basic"]["value"]
                )
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
                    create_choice(name="Kills (default)", value="kills"),
                    create_choice(name="Precision Kills", value="precisionkills"),
                    create_choice(name="% Precision Kills", value="precisionkillspercent"),
                ],
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
                    create_choice(name="Warlock", value="2271682572"),
                    create_choice(name="Hunter", value="671679327"),
                    create_choice(name="Titan", value="3655393761"),
                ],
            ),
            create_option(
                name="starttime",
                description="Format: 'DD/MM/YY' - You can restrict the time from when the weapon stats start counting",
                option_type=3,
                required=False,
            ),
            create_option(
                name="endtime",
                description="Format: 'DD/MM/YY' - You can restrict the time up until which the weapon stats count",
                option_type=3,
                required=False,
            ),
            create_option(
                name="mode",
                description="You can restrict the game mode where the weapon stats count",
                option_type=3,
                required=False,
                choices=choices_mode,
            ),
            create_option(
                name="activityhash",
                description="You can restrict the activity where the weapon stats count (advanced)",
                option_type=4,
                required=False,
            ),
            options_user(),
        ],
    )
    async def _weapon(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)
        destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
        if not destiny_player:
            return

        # get other params
        (
            stat,
            graph,
            character_class,
            mode,
            activity_hash,
            starttime,
            endtime,
        ) = await self._compute_params(ctx, kwargs)
        if not stat:
            return

        # get weapon info
        weapon_name, weapon_hashes = await searchForItem(ctx, kwargs["weapon"])
        if not weapon_name:
            return

        # _update user db
        await destiny_player.update_activity_db()

        # get the char class if that is asked for
        charID = await destiny_player.get_character_id_by_class(character_class) if character_class else None

        # get all weapon infos
        kwargs = {
            "characterID": charID,
            "mode": mode,
            "activityID": activity_hash,
            "start": starttime,
            "end": endtime,
        }

        # loop through every variant of the weapon and add that together
        result = []
        for entry in weapon_hashes:
            result.extend(
                await getWeaponInfo(
                    destiny_player.destiny_id,
                    entry,
                    **{k: v for k, v in kwargs.items() if v is not None},
                )
            )

        # throw error if no weapon
        if not result:
            await ctx.send(embed=embed_message("Error", f"No weapon stats found for {weapon_name}"))
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
            embed = embed_message(f"{weapon_name} stats for {user.display_name}")
            embed.add_field(name="Total Kills", value=f"**{kills:,}**", inline=True)
            embed.add_field(
                name="Total Precision Kills",
                value=f"**{precision_kills:,}**",
                inline=True,
            )
            embed.add_field(
                name="% Precision Kills",
                value=f"**{round(percent_precision_kills * 100, 2)}%**",
                inline=True,
            )
            embed.add_field(
                name="Average Kills",
                value=f"**{round(avg_kills, 2)}**\nIn {len(result)} Activities",
                inline=True,
            )
            embed.add_field(
                name="Maximum Kills",
                value=f"**{max_kills:,}**\nIn Activity ID: {max_kills_id}\n{max_kills_mode} - {max_kills_name}\nOn: {max_kills_date.strftime('%d/%m/%y')}",
                inline=True,
            )
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
            for (
                instance_time,
                uniqueweaponkills,
                uniqueweaponprecisionkills,
            ) in weapon_hashes:
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
                        "datetime": time.date(),
                        "statistic": statistic2 / statistic1 if stat == "precisionkillspercent" else statistic1,
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
                "datetime": time,
                "statistic": statistic2 / statistic1 if stat == "precisionkillspercent" else statistic1,
            }
            df = df.append(entry, ignore_index=True)

            # convert to correct file types
            df["datetime"] = pd.to_datetime(df["datetime"])
            df["statistic"] = pd.to_numeric(df["statistic"])

            # building the graph
            # Create figure and plot space
            fig, ax = plt.subplots(figsize=(20, 10))
            ax.yaxis.grid(True)

            # filling bar chart
            ax.bar(df["datetime"], df["statistic"], color="#45b6fe")

            # Set title and labels for axes
            ax.set_title(
                f"{weapon_name} stats for {user.display_name}",
                fontweight="bold",
                size=30,
                pad=20,
            )
            ax.set_xlabel("Date", fontsize=20)
            ax.set_ylabel(name, fontsize=20)

            # saving file
            title = "weapon.png"
            plt.savefig(title)

            # sending them the file
            await ctx.send(file=discord.File(title))

            # _delete file
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
                    create_choice(name="Kills (default)", value="kills"),
                    create_choice(name="Precision Kills", value="precisionkills"),
                    create_choice(name="% Precision Kills", value="precisionkillspercent"),
                ],
            ),
            create_option(
                name="class",
                description="You can restrict the class where the weapon stats count",
                option_type=3,
                required=False,
                choices=[
                    create_choice(name="Warlock", value="2271682572"),
                    create_choice(name="Hunter", value="671679327"),
                    create_choice(name="Titan", value="3655393761"),
                ],
            ),
            create_option(
                name="expansion",
                description="You can restrict the expansion (usually a year) to look at",
                option_type=3,
                required=False,
                choices=[
                    create_choice(name=expansion[1], value=f"{expansion[0]},{expansion[1]}")
                    for expansion in expansion_dates
                ],
            ),
            create_option(
                name="season",
                description="You can restrict the season to look at",
                option_type=3,
                required=False,
                choices=[create_choice(name=season[1], value=f"{season[0]},{season[1]}") for season in season_dates],
            ),
            create_option(
                name="starttime",
                description="Format: 'DD/MM/YY' - You can restrict the time from when the weapon stats start counting",
                option_type=3,
                required=False,
            ),
            create_option(
                name="endtime",
                description="Format: 'DD/MM/YY' - You can restrict the time up until which the weapon stats count",
                option_type=3,
                required=False,
            ),
            create_option(
                name="mode",
                description="You can restrict the game mode where the weapon stats count",
                option_type=3,
                required=False,
                choices=choices_mode,
            ),
            create_option(
                name="activityhash",
                description="You can restrict the activity where the weapon stats count (advanced)",
                option_type=4,
                required=False,
            ),
            options_user(),
        ],
    )
    async def _topweapons(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)
        destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
        if not destiny_player:
            return

        # get other params
        (
            stat,
            _,
            character_class,
            mode,
            activity_hash,
            starttime,
            endtime,
        ) = await self._compute_params(ctx, kwargs)
        if not stat:
            return

        # get the real weapon name if that param is given
        weapon_name = None
        if "weapon" in kwargs:
            weapon_name, weapon_id = await searchForItem(ctx, kwargs["weapon"])
            weapon_id = weapon_id[0]
            if not weapon_name:
                return

        # might take a sec
        if not ctx.deferred:
            await ctx.defer()

        # _update user db
        await destiny_player.update_activity_db()

        # get the char class if that is asked for
        charID = await destiny_player.get_character_id_by_class(character_class) if character_class else None

        # get all weaponID infos
        kwargs = {
            "characterID": charID,
            "mode": mode,
            "activityID": activity_hash,
            "start": starttime,
            "end": endtime,
        }
        result = await getTopWeapons(
            destiny_player.destiny_id,
            **{k: v for k, v in kwargs.items() if v is not None},
        )

        # loop through all weapons and divide them into kinetic / energy / power
        weapons_by_slot = {
            "Kinetic": [],
            "Energy": [],
            "Power": [],
        }
        for weapon in result:
            if stat == "kills":
                statistic_data = weapon[1]
                statistic_visual = f"{statistic_data:,}"
            elif stat == "precisionkills":
                statistic_data = weapon[2]
                statistic_visual = f"{statistic_data:,}"
            else:  # precisionkillspercent
                statistic_data = weapon[1] / weapon[2] if weapon[2] != 0 else 0
                statistic_visual = f"{round(statistic_data * 100, 2)}%"

            weapons_by_slot[translateWeaponSlot(weapon[4])].append(
                {
                    "weapon_id": weapon[0],
                    "weapon_name": weapon[3],
                    "weapon_stat": statistic_data,
                    "weapon_stat_visual": statistic_visual,
                }
            )

        # prepare embed
        embed = embed_message(
            f"Top Weapons for {user.display_name}",
            footer=f"""Date: {starttime.strftime("%d/%m/%Y")} - {endtime.strftime("%d/%m/%Y")}""",
        )
        emoji = self.client.get_emoji(enter_emoji_id)

        # loop through the slots
        found = False if weapon_name else True
        for slot, weapons in weapons_by_slot.items():
            # sort the slots
            sorted_weapons = sorted(weapons, key=lambda x: x["weapon_stat"], reverse=True)

            # loop through the weapons
            i = 0
            max_weapons = 8
            ranking = []
            for weapon in sorted_weapons:
                i += 1
                if len(ranking) < max_weapons:
                    # setting a flag if name is in list
                    if weapon_name == weapon["weapon_name"]:
                        found = True
                        ranking.append(
                            write_line(
                                i,
                                f"""**[{weapon["weapon_name"]}](https://www.light.gg/db/items/{weapon["weapon_id"]})**""",
                                stat.capitalize(),
                                weapon["weapon_stat_visual"],
                                emoji,
                            )
                        )
                    else:
                        ranking.append(
                            write_line(
                                i,
                                f"""[{weapon["weapon_name"]}](https://www.light.gg/db/items/{weapon["weapon_id"]})""",
                                stat.capitalize(),
                                weapon["weapon_stat_visual"],
                                emoji,
                            )
                        )

                # looping through rest until original user is found
                elif (len(ranking) >= max_weapons) and (not found):
                    # adding only this name
                    if weapon_name == weapon["weapon_name"]:
                        ranking.append("...")
                        ranking.append(
                            write_line(
                                i,
                                f"""[{weapon["weapon_name"]}](https://www.light.gg/db/items/{weapon["weapon_id"]})""",
                                stat.capitalize(),
                                weapon["weapon_stat_visual"],
                                emoji,
                            )
                        )
                        found = True
                        break

                else:
                    break

            # write that info in an embed field
            embed.add_field(name=slot, value="\n".join(ranking), inline=True)

        # write a message in the embed, since it is not in there
        if not found:
            embed.description = f"No stats found for `{weapon_name}`, here are your top weapons anyways"

        # post embed
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
            await ctx.send(
                hidden=True,
                embed=embed_message(f"Error", f"The argument `activityhash` must be a number"),
            )
            return None, None, None, None, None, None, None

        # parse the three different time arguments, since they are mutually exclusive
        if not check_if_mutually_exclusive(["expansion", "season", ["starttime", "endtime"]], kwargs):
            await ctx.send(
                hidden=True,
                embed=embed_message(f"Error", f"You can only specify one time parameter"),
            )
            return None, None, None, None, None, None, None

        # make sure the times are valid
        starttime = (
            await verify_time_input(ctx, kwargs["starttime"]) if "starttime" in kwargs else datetime.datetime.min
        )
        if not starttime:
            return None, None, None, None, None, None, None
        endtime = await verify_time_input(ctx, kwargs["endtime"]) if "endtime" in kwargs else datetime.datetime.now()
        if not endtime:
            return None, None, None, None, None, None, None

        # convert expansion dates to datetimes
        dummy_starttime, dummy_endtime = convert_expansion_or_season_dates(kwargs)
        if dummy_starttime:
            starttime = dummy_starttime
            endtime = dummy_endtime

        return stat, graph, character_class, mode, activity_hash, starttime, endtime

    @cog_ext.cog_slash(
        name="meta",
        description="Displays most used weapons by clanmembers (Default: in the last 30 days)",
        options=[
            create_option(
                name="class",
                description="You can restrict the class where the weapon stats count",
                option_type=3,
                required=False,
                choices=[
                    create_choice(name="Warlock", value="2271682572"),
                    create_choice(name="Hunter", value="671679327"),
                    create_choice(name="Titan", value="3655393761"),
                ],
            ),
            create_option(
                name="expansion",
                description="You can restrict the expansion (usually a year) to look at",
                option_type=3,
                required=False,
                choices=[
                    create_choice(name=expansion[1], value=f"{expansion[0]},{expansion[1]}")
                    for expansion in expansion_dates
                ],
            ),
            create_option(
                name="season",
                description="You can restrict the season to look at",
                option_type=3,
                required=False,
                choices=[create_choice(name=season[1], value=f"{season[0]},{season[1]}") for season in season_dates],
            ),
            create_option(
                name="starttime",
                description="Format: 'DD/MM/YY' - You can restrict the time from when the weapon stats start counting",
                option_type=3,
                required=False,
            ),
            create_option(
                name="endtime",
                description="Format: 'DD/MM/YY' - You can restrict the time up until which the weapon stats count",
                option_type=3,
                required=False,
            ),
            create_option(
                name="mode",
                description="You can restrict the game mode (Default: Everything)",
                option_type=3,
                required=False,
                choices=choices_mode,
            ),
            create_option(
                name="activityhash",
                description="You can restrict the activity (advanced)",
                option_type=4,
                required=False,
            ),
        ],
    )
    async def _meta(self, ctx: SlashContext, **kwargs):
        weapons_by_slot = {
            "Kinetic": {},
            "Energy": {},
            "Power": {},
        }
        weapons_by_id = {}

        # set default values for the args
        character_class = int(kwargs["class"]) if "class" in kwargs else None
        mode = int(kwargs["mode"]) if "mode" in kwargs else 0
        try:
            activity_hash = int(kwargs["activityhash"]) if "activityhash" in kwargs else None
        except ValueError:
            await ctx.send(
                hidden=True,
                embed=embed_message(f"Error", f"The argument `activityhash` must be a number"),
            )
            return

        # parse the three different time arguments, since they are mutually exclusive
        if not check_if_mutually_exclusive(["expansion", "season", ["starttime", "endtime"]], kwargs):
            await ctx.send(
                hidden=True,
                embed=embed_message(f"Error", f"You can only specify one time parameter"),
            )
            return

        # if given, make sure the times are valid
        starttime = (
            await verify_time_input(ctx, kwargs["starttime"])
            if "starttime" in kwargs
            else datetime.datetime.now() - datetime.timedelta(days=30)
        )
        if not starttime:
            return
        endtime = await verify_time_input(ctx, kwargs["endtime"]) if "endtime" in kwargs else datetime.datetime.now()
        if not endtime:
            return

        # convert expansion dates to datetimes
        dummy_starttime, dummy_endtime = convert_expansion_or_season_dates(kwargs)
        if dummy_starttime:
            starttime = dummy_starttime
            endtime = dummy_endtime

        # might take a sec
        await ctx.defer()

        # loop through all users and get their stats
        clan_members = await getClanMembers(self.client)
        result = await asyncio.gather(
            *[
                self._handle_user(
                    await DestinyPlayer.from_destiny_id(destinyID),
                    mode,
                    activity_hash,
                    starttime,
                    endtime,
                    character_class,
                )
                for destinyID in clan_members
            ]
        )

        for clan_member in result:
            if clan_member is not None:
                for weapon in clan_member:
                    translated_weapon_slot = translateWeaponSlot(weapon[4])
                    try:
                        weapons_by_slot[translated_weapon_slot].update(
                            {weapon[0]: weapons_by_slot[translated_weapon_slot][weapon[0]] + weapon[1]}
                        )
                    except KeyError:
                        weapons_by_slot[translated_weapon_slot].update({weapon[0]: weapon[1]})
                        weapons_by_id.update({weapon[0]: weapon[3]})

        # prepare embed
        embed = embed_message(
            "Clanmember Weapon Meta",
            footer=f"Date: {starttime.strftime('%d/%m/%Y')} - {endtime.strftime('%d/%m/%Y')}",
        )

        # loop through the slots and write the text
        emoji = self.client.get_emoji(enter_emoji_id)
        for slot, weapons in weapons_by_slot.items():
            # sort it and only get the first 8 slots
            sorted_weapons = dict(sorted(weapons.items(), key=lambda x: x[1], reverse=True)[:8])

            # loop through the top
            slot_text = []
            i = 1
            for weapon_id, weapon_kills in sorted_weapons.items():
                text = write_line(
                    i,
                    f"[{weapons_by_id[weapon_id]}](https://www.light.gg/db/items/{weapon_id})",
                    "Kills",
                    f"{weapon_kills:,}",
                    emoji,
                )
                slot_text.append(text)
                i += 1

            # write that info in an embed field
            embed.add_field(name=slot, value="\n".join(slot_text), inline=True)

        # post embed
        await ctx.send(embed=embed)

    async def _handle_user(
        self,
        destiny_player: Optional[DestinyPlayer],
        mode,
        activity_hash,
        starttime,
        endtime,
        character_class,
    ):
        # get character id if asked for
        charID = await destiny_player.get_character_id_by_class(character_class) if character_class else None

        # get all weapon kills
        kwargs = {
            "characterID": charID,
            "mode": mode,
            "activityID": activity_hash,
            "start": starttime,
            "end": endtime,
        }
        return await getTopWeapons(
            destiny_player.destiny_id,
            **{k: v for k, v in kwargs.items() if v is not None},
        )


class TournamentCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.creator = None

    @cog_ext.cog_subcommand(
        base="tournament",
        base_description="Everything you need for in-house PvP tournaments",
        name="_insert",
        description="Opens up registration. Can only be used if no other tournament is currently running",
    )
    async def _create(self, ctx: SlashContext):
        # check if tourn already exists
        message = await get_persistent_message_or_channel(self.client, "tournament", ctx.guild.id)
        if message:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    f"Error",
                    f"A tournament already exists. \nPlease wait until it is completed and then try again or ask a member of staff to _delete it",
                ),
            )
            return

        # get the tourn channel id
        channel = (await get_persistent_message_or_channel(self.client, "tournamentChannel", ctx.guild.id)).channel

        # make registration message
        embed = embed_message(
            "Registration",
            f"{ctx.author.display_name} startet a tournament!\nTo enter it, please react accordingly",
        )
        await make_persistent_message(
            self.client,
            "tournament",
            ctx.guild.id,
            channel.id,
            reaction_id_list=tournament,
            message_embed=embed,
        )

        # to remember who started the tournament, we set ctx.author as the message author
        self.creator = ctx.author

        # let user know
        await ctx.send(
            embed=embed_message(
                "Success",
                f"Registration for the tournament has started, visit {channel.mention} to join the fun!",
            )
        )

    @cog_ext.cog_subcommand(
        base="tournament",
        base_description="Everything you need for in-house PvP tournaments",
        name="start",
        description="Starts the tournament. Can only be used by the user who used '/tournament _insert' or an Admin",
    )
    async def _start(self, ctx: SlashContext):
        # check if tourn exists
        message = await get_persistent_message_or_channel(self.client, "tournament", ctx.guild.id)
        if not message:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    f"Error",
                    f"You need to start the registration by using `/tournament _insert` first",
                ),
            )
            return

        # check if author has permissions to start
        if not (message.author == ctx.author) and not (await has_elevated_permissions(ctx.author, ctx.guild)):
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    f"Error",
                    f"Only admins and the tournament creator can start the tournament",
                ),
            )
            return

        # check that at least two people (3, since bot counts too) have reacted and get the users
        for reaction in message.reactions:
            if reaction.emoji.id in tournament:
                if reaction.count < 3:
                    await ctx.send(
                        hidden=True,
                        embed=embed_message(f"Error", f"At least two people need to sign up"),
                    )
                    return
                participants = []
                async for user in reaction.users():
                    if not user.bot:
                        participants.append(user)

        # start the tourn and wait for it to play out
        await ctx.send(embed=embed_message("Success", "The tournament is now starting"))
        winner = await startTournamentEvents(self.client, message, message.channel, participants)

        # _delete registration message
        channel = message.channel
        await delete_persistent_message(message, "tournament", ctx.guild.id)

        # announce winner
        embed = embed_message("We have a winner", f"Congratulation {winner.mention}!")
        msg = await channel.send(embed=embed)

        # wait 10 mins and then _delete
        await asyncio.sleep(60 * 10)
        await msg._delete()

    @cog_ext.cog_subcommand(
        base="tournament",
        base_description="Everything you need for in-house PvP tournaments",
        name="_delete",
        description="Delete the tournament. Can only be used by the user who used '/tournament _insert' or an Admin",
    )
    async def _delete(self, ctx: SlashContext):
        # check if tourn exists
        message = await get_persistent_message_or_channel(self.client, "tournament", ctx.guild.id)
        if not message:
            await ctx.send(
                hidden=True,
                embed=embed_message(f"Error", f"There is no tournament to _delete"),
            )
            return

        # check if author has permissions to start
        if not (message.author == ctx.author) and not (await has_elevated_permissions(ctx.author, ctx.guild)):
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    f"Error",
                    f"Only admins and the tournament creator can _delete the tournament",
                ),
            )
            return

        # _delete msg
        await delete_persistent_message(message, "tournament", ctx.guild.id)

        await ctx.send(embed=embed_message("Success", "The tournament has been deleted"))


def setup(client):
    client.add_cog(DestinyCommands(client))
    client.add_cog(MysticCommands(client))
    client.add_cog(RankCommands(client))
    client.add_cog(WeaponCommands(client))
    client.add_cog(ClanActivitiesCommands(client))
    client.add_cog(TournamentCommands(client))
