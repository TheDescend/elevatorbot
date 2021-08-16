import asyncio
import copy
import datetime
import io
import pickle

import aiohttp
import discord
import pytz
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

from ElevatorBot.functions.destinyPlayer import DestinyPlayer
from ElevatorBot.functions.formating import embed_message
from ElevatorBot.networking.network import get_json_from_url
from ElevatorBot.static.config import CLANID
from ElevatorBot.static.globals import member_role_id, clan_role_id
from ElevatorBot.static.slashCommandConfig import permissions_kigstn


class Day1Race(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="day1race",
        description="Starts the Day One raid completion announcer",
        default_permission=False,
        permissions=permissions_kigstn,
    )
    async def _day1race(self, ctx: SlashContext):
        channel = ctx.channel
        await ctx.send("Done", hidden=True)

        # >>> CHANGE HERE FOR DIFFERENT DAY 1 HASHES <<<
        # only change the vog only stuff further down, just search "vog only stuff from here on"
        leaderboard_channel = 837622568152203304
        self.activity_triumph = 2384429092
        self.activity_triumph_encounters = {
            4240665: "First Raid Run",
            4240664: "Conflux Challenge",
            4240667: "Oracle Challenge",
            4240666: "Templar Challenge",
            4240669: "Gatekeeper Challenge",
            4240668: "Atheon Challenge",
        }
        self.alternative_activity_triumph = 3114569402
        self.activity_metric = 2506886274
        self.activity_hashes = [1485585878, 3711931140, 3881495763]
        self.emblem_collectible_hash = 2172413746
        start = datetime.datetime(2021, 5, 22, 17, 0, tzinfo=datetime.timezone.utc)
        cutoff_time = datetime.datetime(
            2021, 5, 23, 17, 0, tzinfo=datetime.timezone.utc
        )
        image_url = "https://static.wikia.nocookie.net/destinypedia/images/6/62/Vault.jpg/revision/latest/scale-to-width-down/1000?cb=20150330170833"
        raid_name = "Vault of Glass"
        location_name = "Ishtar Sink, Venus"

        # printing the raid image. Taken from data.destinysets.com
        activity_name = f"{location_name} - {raid_name}"
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    data = io.BytesIO(await resp.read())
                    await channel.send(
                        f"__**{activity_name}**__\nMy day one mode is now activated and I will (hopefully) inform about completions. \nGood luck to everyone competing, will see you on the other side."
                    )
                    await channel.send(file=discord.File(data, f"raid_image.png"))

        self.leaderboard_msg = None
        self.leaderboard_channel = self.client.get_channel(leaderboard_channel)

        self.finished_encounters_blueprint = {}
        for encounter in self.activity_triumph_encounters:
            self.finished_encounters_blueprint[encounter] = 0

        self.clan_members = (
            await get_json_from_url(
                f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"
            )
        ).content["Response"]["results"]

        try:
            with open(f"{raid_name}_finished_encounters.pickle", "rb") as handle:
                self.finished_encounters = pickle.load(handle)
            with open(f"{raid_name}_finished_raid.pickle", "rb") as handle:
                self.finished_raid = pickle.load(handle)
        except FileNotFoundError:
            self.finished_raid = {}
            self.finished_encounters = {}
            for member in self.clan_members:
                destinyID = int(member["destinyUserInfo"]["membershipId"])
                self.finished_encounters[destinyID] = copy.deepcopy(
                    self.finished_encounters_blueprint
                )

        # loop until raid race is done
        now = datetime.datetime.now(datetime.timezone.utc)
        while cutoff_time > now:
            # gets all online users. Returns list with tuples (name, destinyID)
            online = []
            for member in (
                await get_json_from_url(
                    f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"
                )
            ).content["Response"]["results"]:
                if member["isOnline"]:
                    online.append(
                        (
                            member["destinyUserInfo"]["LastSeenDisplayName"],
                            int(member["destinyUserInfo"]["membershipId"]),
                        )
                    )

            # loops through all online users
            result = await asyncio.gather(
                *[self.look_for_completion(member, channel) for member in online]
            )
            for res in result:
                if res is not None:
                    # check if all encounters are complete and if so save that
                    all_done = True
                    for encounter, complete in self.finished_encounters[res[1]].items():
                        if complete == 0:
                            all_done = False
                            break
                    if all_done:
                        self.finished_raid[res] = now

            # update leaderboard message
            await self.update_leaderboard()

            # save data as pickle
            with open(f"{raid_name}_finished_encounters.pickle", "wb") as handle:
                pickle.dump(self.finished_encounters, handle)
            with open(f"{raid_name}_finished_raid.pickle", "wb") as handle:
                pickle.dump(self.finished_raid, handle)

            # wait 1 min before checking again
            await asyncio.sleep(60)

            # set new now
            now = datetime.datetime.now(datetime.timezone.utc)
            print(f"Done with loop at {str(now)}")

        # write the completion message
        if self.finished_raid:
            # get total time spend in raid
            completions = []
            for member in self.finished_raid:
                name = member[0]
                destiny_player = await DestinyPlayer.from_discord_id(member[1])

                # loop though activities
                time_spend = 0
                kills = 0
                deaths = 0
                try:
                    async for activity in destiny_player.get_activity_history(mode=4):
                        period = datetime.datetime.strptime(
                            activity["period"], "%Y-%m-%dT%H:%M:%SZ"
                        )
                        tz_period = pytz.utc.localize(period)

                        if tz_period < start:
                            continue
                        if tz_period > cutoff_time:
                            continue

                        if (
                            activity["activityDetails"]["directorActivityHash"]
                            in self.activity_hashes
                        ):
                            time_spend += activity["values"]["timePlayedSeconds"][
                                "basic"
                            ]["value"]
                            kills += activity["values"]["kills"]["basic"]["value"]
                            deaths += activity["values"]["deaths"]["basic"]["value"]

                    # write the fancy text
                    completions.append(
                        f"""<:desc_circle_b:768906489464619008>**{name}** - Kills: *{int(kills):,}*, Deaths: *{int(deaths):,}*, Time: *{str(datetime.timedelta(seconds=time_spend))}*"""
                    )
                except:
                    print(f"Failed member {name}")
                    completions.append(
                        f"""<:desc_circle_b:768906489464619008>**{name}** finished the raid, but there is no info in the API yet"""
                    )

            completion_text = "\n".join(completions)
            msg = f"""The raid race is over :(. But some clan members managed to get a completion!\n⁣\n<:desc_logo_b:768907515193720874> __**Completions:**__\n{completion_text}"""
        else:
            msg = "Sadly nobody here finished the raid in time, good luck next time!"

        embed = embed_message("Raid Race Summary", msg)

        stats = await channel.send(embed=embed)
        await stats.pin()

    async def look_for_completion(self, member, channel):
        try:
            name = member[0]
            destiny_player = await DestinyPlayer.from_destiny_id(member[1])

            if member not in self.finished_raid:
                records = await destiny_player.get_triumphs()
                record_list = []
                try:
                    """vog only stuff from here on. Vog triumph is class specific"""
                    for char in records["characterRecords"]["data"].values():
                        record_list.append(char["records"][str(self.activity_triumph)])
                except KeyError:
                    pass

                # check each encounter
                if record_list:
                    for (
                        encounter_hash,
                        description,
                    ) in self.activity_triumph_encounters.items():
                        br = False
                        for record in record_list:
                            if br:
                                break

                            # abort if user has already completed that encounter
                            if (
                                self.finished_encounters[destiny_player.destiny_id][
                                    encounter_hash
                                ]
                                == 0
                            ):
                                for record_objective_hash in record["objectives"]:
                                    if (
                                        encounter_hash
                                        == record_objective_hash["objectiveHash"]
                                    ):
                                        # check if is complete
                                        if record_objective_hash["complete"]:
                                            self.finished_encounters[
                                                destiny_player.destiny_id
                                            ][encounter_hash] = 1
                                            await channel.send(
                                                f"**{name}** finished `{description}` <:PeepoDPS:754785311489523754>"
                                            )
                                            br = True
                                        break

                """ vog only stuff from here on. Change that back if a raid comes out which you dont need to finish twice """
                # check if a completion was counted via the triumph. if not, look at the other triumph to at least set first completion as done
                if (
                    self.finished_encounters_blueprint
                    == self.finished_encounters[destiny_player.destiny_id]
                ):
                    try:
                        record2 = records["profileRecords"]["data"]["records"][
                            str(self.alternative_activity_triumph)
                        ]
                    except KeyError:
                        record2 = None
                    if record2:
                        for record_objective_hash in record2["objectives"]:
                            if record_objective_hash["complete"]:
                                self.finished_encounters[destiny_player.destiny_id][
                                    4240665
                                ] = 1
                                await channel.send(
                                    f"**{name}** finished `{self.activity_triumph_encounters[4240665]}` <:PeepoDPS:754785311489523754>"
                                )
                                break

                # check if a completion was counted via the triumph. if not, look at the metric to at least set first completion as done
                if (
                    self.finished_encounters_blueprint
                    == self.finished_encounters[destiny_player.destiny_id]
                ):
                    metric_completions = await destiny_player.get_metric_value(
                        self.activity_metric
                    )
                    if metric_completions > 0:
                        self.finished_encounters[destiny_player.destiny_id][4240665] = 1
                        await channel.send(
                            f"**{name}** finished `{self.activity_triumph_encounters[4240665]}` <:PeepoDPS:754785311489523754>"
                        )

                # check for the emblem, if exist do the msg for every other encounter done
                has_emblem = await destiny_player.has_collectible(
                    self.emblem_collectible_hash
                )
                if has_emblem:
                    for (
                        encounter_hash,
                        description,
                    ) in self.activity_triumph_encounters.items():
                        if (
                            self.finished_encounters[destiny_player.destiny_id][
                                encounter_hash
                            ]
                            == 0
                        ):
                            self.finished_encounters[destiny_player.destiny_id][
                                encounter_hash
                            ] = 1
                            await channel.send(
                                f"**{name}** finished `{description}` <:PeepoDPS:754785311489523754>"
                            )

                """ vog only stuff over """
        except Exception as e:
            print(e)

        return member

    async def update_leaderboard(self):
        running_raid = {}

        # loop through clan members
        for member in self.clan_members:
            destinyID = int(member["destinyUserInfo"]["membershipId"])
            name = member["destinyUserInfo"]["LastSeenDisplayName"]

            # only check if member did not finish the raid. loop through their encounter completion
            if (name, destinyID) not in self.finished_raid:
                for encounter, complete in self.finished_encounters[destinyID].items():
                    if complete == 1:
                        try:
                            running_raid[(name, destinyID)].append(
                                self.activity_triumph_encounters[encounter]
                            )
                        except KeyError:
                            running_raid[(name, destinyID)] = [
                                self.activity_triumph_encounters[encounter]
                            ]

        embed = embed_message(
            "Race for Worlds First / Day One",
            "First results are in! These are the current result:",
            "Note: If progress does not show up, the API might not show the info. Nothing I can do :(",
        )

        if self.finished_raid:
            embed.add_field(name="⁣", value=f"__Finished:__", inline=False)

            sort = {
                k: v
                for k, v in sorted(
                    self.finished_raid.items(), key=lambda item: item[1], reverse=False
                )
            }
            times = []
            names = []
            for key, value in sort.items():
                names.append(key[0])
                times.append(
                    f"{value.day}/{value.month} - {value.hour}:{value.minute:02d} UTC"
                )

            embed.add_field(name="Name", value="\n".join(names), inline=True)
            embed.add_field(name="Time", value="\n".join(times), inline=True)

        if running_raid:
            embed.add_field(name="⁣", value=f"__Running:__", inline=False)

            sort = {
                k: v
                for k, v in sorted(
                    running_raid.items(), key=lambda item: len(item[1]), reverse=True
                )
            }
            done = []
            names = []
            for key, value in sort.items():
                names.append(key[0])
                done.append(", ".join(value))

            embed.add_field(name="Name", value="\n".join(names), inline=True)
            embed.add_field(name="Completed", value="\n".join(done), inline=True)

        if self.finished_raid or running_raid:
            if not self.leaderboard_msg:
                try:
                    self.leaderboard_msg = await self.leaderboard_channel.send(
                        embed=embed
                    )
                except:
                    pass
            else:
                await self.leaderboard_msg.edit(embed=embed)

    @cog_ext.cog_slash(
        name="day1completions",
        description="Returns a list of everyone who has completed the specified raid on Day One",
        options=[
            create_option(
                name="raid",
                description="The name of the raid",
                option_type=3,
                required=True,
                choices=[
                    create_choice(name="Last Wish", value="Last Wish"),
                    create_choice(
                        name="Scourge of the Past", value="Scourge of the Past"
                    ),
                    create_choice(name="Crown of Sorrows", value="Crown of Sorrows"),
                    create_choice(
                        name="Garden of Salvation", value="Garden of Salvation"
                    ),
                    create_choice(name="Deep Stone Crypt", value="Deep Stone Crypt"),
                    create_choice(name="Vault of Glass", value="Vault of Glass"),
                ],
            ),
        ],
    )
    async def _day1completions(self, ctx: SlashContext, raid: str):
        raid_to_emblem_hash = {
            "Last Wish": 1171206947,
            "Scourge of the Past": 2473783710,
            "Crown of Sorrows": 3171386140,
            "Garden of Salvation": 3938759711,
            "Deep Stone Crypt": 2273453972,
            "Vault of Glass": 2172413746,
        }

        await ctx.defer()

        member_role = ctx.guild.get_role(member_role_id)
        clan_role = ctx.guild.get_role(clan_role_id)

        self.clan_list = []
        self.user_list = []

        async def check_member(member):
            if member_role in member.roles:
                destiny_player = await DestinyPlayer.from_discord_id(member.id)
                if destiny_player:
                    if await destiny_player.has_collectible(
                        str(raid_to_emblem_hash[raid])
                    ):
                        if clan_role in member.roles:
                            self.clan_list.append(member.display_name)
                        else:
                            self.user_list.append(member.display_name)

        await asyncio.gather(*[check_member(member) for member in ctx.guild.members])

        embed = embed_message(f"{raid} - Day One Completions")

        if not self.clan_list and not self.user_list:
            embed.description = "Sadly nobody here cleared this raid :("

        if self.clan_list:
            embed.add_field(
                name="Clan Members", value="\n".join(self.clan_list), inline=True
            )

        if self.user_list:
            embed.add_field(
                name="Other People", value="\n".join(self.user_list), inline=True
            )

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Day1Race(client))
