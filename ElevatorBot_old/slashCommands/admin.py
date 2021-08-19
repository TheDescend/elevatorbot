import asyncio
import datetime
import random

from discord.ext import commands
from discord_slash import cog_ext, SlashContext, ButtonStyle
from discord_slash.utils import manage_components
from discord_slash.utils.manage_commands import create_option, create_choice

from ElevatorBot.database.database import lookupDiscordID
from ElevatorBot.core.dataLoading import getNameAndCrossaveNameToHashMapByClanid
from ElevatorBot.core.destinyPlayer import DestinyPlayer
from ElevatorBot.core.formating import embed_message
from ElevatorBot.core.persistentMessages import (
    make_persistent_message,
    steamJoinCodeMessage,
)
from ElevatorBot.core.roleLookup import assignRolesToUser, removeRolesFromUser
from ElevatorBot.networking.bungieAuth import handle_and_return_token
from ElevatorBot.networking.network import get_json_from_url
from ElevatorBot.static.config import CLANID
from ElevatorBot.static.globals import (
    other_game_roles,
    muted_role_id,
    bot_spam_channel_id,
    enter_emoji_id,
    circle_emoji_id,
)
from ElevatorBot.static.slashCommandConfig import (
    permissions_admin,
    permissions_kigstn_hali,
)


class AdminCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="getnaughtyclanmembers",
        description="Blames people who are in the D2 clan, but do not fulfill our requirements",
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _getnaughtyclanmembers(self, ctx: SlashContext):
        await ctx.send(
            hidden=True,
            embed=embed_message(
                "Please wait...", "The results will be here in a second"
            ),
        )

        # get all clan members discordID
        memberlist = []
        for member in (
            await get_json_from_url(
                f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"
            )
        ).content["Response"]["results"]:
            destinyID = int(member["destinyUserInfo"]["membershipId"])
            memberlist.append(destinyID)

        not_in_discord_or_registered = []  # list of destinyID
        no_token = []  # list of guild.member.mention
        not_accepted_rules = []  # list of guild.member.mention

        # loop through all members and check requirements
        for destinyID in memberlist:
            # check if in discord or still having the old force registration
            discordID = await lookupDiscordID(destinyID)
            if discordID is None:
                not_in_discord_or_registered.append(str(destinyID))
                continue
            member = ctx.guild.get_member(discordID)
            if member is None:
                not_in_discord_or_registered.append(str(destinyID))
                continue

            # check if no token
            if not (await handle_and_return_token(discordID)).token:
                no_token.append(member.mention)

            # check if accepted rules
            if member.pending:
                not_accepted_rules.append(member.mention)

        if not_in_discord_or_registered:
            textstr = ", ".join(not_in_discord_or_registered)
            while tempstr := textstr[:1900]:
                await ctx.channel.send(
                    "**These destinyIDs are not in discord, or have not registered with the bot**\n"
                    + tempstr
                )
                textstr = textstr[1900:]

        if no_token:
            textstr = ", ".join(no_token)
            while tempstr := textstr[:1900]:
                await ctx.channel.send(
                    "**These users have no token and need to register with the bot** \n"
                    + tempstr
                )
                textstr = textstr[1900:]

        if not_accepted_rules:
            textstr = ", ".join(not_accepted_rules)
            while tempstr := textstr[:1900]:
                await ctx.channel.send(
                    "**These users have not yet accepted the rules**\n" + tempstr
                )
                textstr = textstr[1900:]

    @cog_ext.cog_slash(
        name="getapikey",
        description="Get your API key",
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _getapikey(self, ctx: SlashContext):
        await ctx.send(
            hidden=True,
            embed=embed_message(
                "Your API Key", (await handle_and_return_token(ctx.author.id)).token
            ),
        )

    @cog_ext.cog_slash(
        name="getusermatching",
        description="Matches in-game and Discord names",
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _getUserMatching(self, ctx: SlashContext):
        await ctx.send(
            hidden=True,
            embed=embed_message(
                "Please wait...", "The results will be here in a second"
            ),
        )

        clanmap = await getNameAndCrossaveNameToHashMapByClanid(CLANID)
        successfulMatches = []
        unsuccessfulMatches = []
        for userid, (steamname, crosssavename) in clanmap.items():
            discordID = await lookupDiscordID(int(userid))
            if discordID:
                # user could be matched
                guy = self.client.get_user(discordID)
                if guy:
                    successfulMatches.append((steamname, crosssavename, guy.name))
                else:
                    await ctx.channel.send(
                        f"[ERROR] {steamname}/{crosssavename} with destinyID {userid} has discordID {discordID} but it is faulty"
                    )
            else:
                # user not found
                unsuccessfulMatches.append((steamname, crosssavename, userid))

        await ctx.channel.send("SUCCESSFUL MATCHES:")
        sortedSuccessfulMatches = sorted(
            successfulMatches, key=lambda pair: pair[2].lower()
        )
        successfulMessage = ""
        for (steamname, crosssavename, username) in sortedSuccessfulMatches:
            successfulMessage += f"{username:<30} - {steamname} / {crosssavename}\n"

        if len(successfulMessage) < 2000:
            await ctx.channel.send(successfulMessage)
        else:
            remainingMessage = successfulMessage
            while curMessage := remainingMessage[:1900]:
                await ctx.channel.send(curMessage)
                remainingMessage = remainingMessage[1900:]
        await ctx.channel.send("FAILED MATCHES:")
        unsuccessfulMessage = ""
        for (steamname, crosssavename, userid) in unsuccessfulMatches:
            unsuccessfulMessage += f"{steamname} / {crosssavename} (Steam-ID {userid}) could not be found in Discord \n"

        if unsuccessfulMessage:
            await ctx.channel.send(unsuccessfulMessage)
        else:
            await ctx.channel.send("No unsuccessful matches <:PogU:670369128237760522>")

    @cog_ext.cog_slash(
        name="mute",
        description="Mutes specified user for specified time",
        options=[
            create_option(
                name="user",
                description="Which user to mute",
                option_type=6,
                required=True,
            ),
            create_option(
                name="hours",
                description="How many hours to mute the user for",
                option_type=4,
                required=True,
            ),
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _mute(self, ctx: SlashContext, user, hours: int):
        await assignRolesToUser([muted_role_id], user, ctx.guild)

        status = await ctx.send(
            embed=embed_message(
                "Success",
                f"Muted {user.mention} for {hours} hours\nI will edit this message once the time is over",
            )
        )

        await asyncio.sleep(hours * 60 * 60)
        await removeRolesFromUser([muted_role_id], user, ctx.guild)

        await status.edit(
            embed=embed_message("Success", f"{user.mention} is no longer muted")
        )

    @cog_ext.cog_slash(
        name="reply",
        description="Send a message to whoever got tagged above",
        options=[
            create_option(
                name="message",
                description="What message to reply with",
                option_type=3,
                required=True,
            ),
            create_option(
                name="user",
                description="Which user to reply to",
                option_type=6,
                required=False,
            ),
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _reply(self, ctx: SlashContext, message: str, user=None):
        # gets the previous message
        last_ten_messages = await ctx.channel.history(limit=10).flatten()

        if not user:
            is_bot_dm = (
                lambda previousMessage: previousMessage.author == self.client.user
                and previousMessage.mentions
            )
            bot_messages = filter(is_bot_dm, last_ten_messages)

            if not bot_messages:
                await ctx.send(
                    embed=embed_message(
                        "Error", f"There is not recent DM. Please specify a user"
                    )
                )
                return

            most_recent = bot_messages[0]
            mentioned_user = most_recent.mentions[0]
            user = mentioned_user

        await user.send(message)
        await ctx.send(
            embed=embed_message(
                "Success", f"{ctx.author.name} replied\n`{message}`\nto {user.mention}"
            )
        )

    @cog_ext.cog_slash(
        name="rollreaction",
        description="Picks a random reactor from the post above",
        options=[
            create_option(
                name="draws",
                description="How many people to draw",
                option_type=4,
                required=True,
            ),
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _rollreaction(self, ctx: SlashContext, draws: int):
        tmessage = (await ctx.channel.history(limit=1).flatten())[0]
        if not tmessage:
            await ctx.send(
                hidden=True, embed=embed_message("Error", "Getting message failed")
            )
            return

        reactionlist = tmessage.reactions
        userlist = []
        for reaction in reactionlist:
            userlist += await reaction.users().flatten()
        uniqueusers = []
        for u in userlist:
            if u not in uniqueusers:
                uniqueusers.append(u)

        if len(uniqueusers) < draws:
            await ctx.send(
                hidden=True, embed=embed_message("Error", "Not enough reactions found")
            )
            return
        winners = [winner.mention for winner in random.sample(uniqueusers, draws)]
        await ctx.send(
            embed=embed_message("Draw Result", f"Selected users {', '.join(winners)}")
        )

    @cog_ext.cog_slash(
        name="getuserinfo",
        description="Get's database infos for the specified user",
        options=[
            create_option(
                name="discorduser",
                description="Look up a discord user",
                option_type=6,
                required=False,
            ),
            create_option(
                name="destinyid",
                description="Look up a destinyID",
                option_type=3,
                required=False,
            ),
            create_option(
                name="fuzzyname",
                description="If you know how the user is called",
                option_type=3,
                required=False,
            ),
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _getuserinfo(
        self,
        ctx: SlashContext,
        discorduser=None,
        destinyid: str = None,
        fuzzyname: str = None,
    ):
        if (
            (not (discorduser or destinyid or fuzzyname))
            or (discorduser and destinyid)
            or (discorduser and fuzzyname)
            or (destinyid and fuzzyname)
            or (destinyid and discorduser and fuzzyname)
        ):
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Error", "Exactly one of the arguments must be used"
                ),
            )
            return
        await ctx.defer()

        # if discord info is given
        if destinyid:
            try:
                destinyid = int(destinyid)
            except ValueError:
                await ctx.send(
                    embed=embed_message("Error", f"DestinyID must be a number")
                )
                return

            destiny_player = await DestinyPlayer.from_destiny_id(destinyid)
            mentioned_user = destiny_player.get_discord_member(ctx.guild)
            if not mentioned_user:
                await ctx.send(
                    embed=embed_message(
                        "Error",
                        f"I don't know a user with the destinyID `{destiny_player.destiny_id}`",
                    )
                )
                return

        # if destiny id is given
        else:
            mentioned_user = discorduser
            destiny_player = await DestinyPlayer.from_discord_id(mentioned_user.id)
            if not destiny_player:
                await ctx.send(
                    embed=embed_message(
                        "Error",
                        f"I don't know a user with the discordID `{mentioned_user.id}`",
                    )
                )
                return

        title = f"Database Infos for {mentioned_user.display_name}"
        text = f"""DiscordID - `{destiny_player.discord_id}` \nDestinyID: `{destiny_player.destiny_id}` \nSystem - `{destiny_player.system}` \nSteamName - `{(await destiny_player.get_destiny_name_and_last_played())[0]}` \nHasToken - `{await destiny_player.has_token()}`"""

        embed = embed_message(
            title, text if text else f"Possible matches for {fuzzyname}"
        )

        # if fuzzy name is given
        if fuzzyname:
            clansearch = []
            returnjson = await get_json_from_url(
                f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members?nameSearch={fuzzyname}"
            )
            clansearch.append(returnjson)

            for result in clansearch:
                resp = result.content["Response"]
                if not resp["results"]:
                    await ctx.send(
                        embed=embed_message(
                            f"Error", f"No matches found for `{fuzzyname}`"
                        )
                    )
                    return

                i = 0
                for guy in resp["results"]:
                    i += 1
                    steam_name = guy["destinyUserInfo"]["LastSeenDisplayName"]
                    bungie_name = guy["bungieNetUserInfo"]["displayName"]
                    destinyID = int(guy["destinyUserInfo"]["membershipId"])
                    discordID = await lookupDiscordID(destinyID)
                    embed.add_field(
                        name=f"Option {i}",
                        value=f"Discord - <@{discordID}>\nSteamName - {steam_name}\nBungieName - {bungie_name}",
                        inline=False,
                    )

        await ctx.send(embed=embed)


class PersistentMessagesCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="channel",
        description="Make new / replace old persistent messages",
        options=[
            create_option(
                name="channel_type",
                description="The type of the channel",
                option_type=3,
                required=True,
                choices=[
                    create_choice(name="Clan Join Request", value="clanjoinrequest"),
                    create_choice(name="Registration", value="registration"),
                    create_choice(name="Other Game Roles", value="othergameroles"),
                    create_choice(name="Steam Join Codes", value="steamjoincodes"),
                    create_choice(name="Tournament", value="tournament"),
                    create_choice(name="Member Count", value="membercount"),
                    create_choice(name="Booster Count", value="boostercount"),
                    create_choice(name="Looking For Group", value="lfg"),
                    create_choice(
                        name="LFG Voice Channel Category", value="lfgvoicecategory"
                    ),
                    create_choice(name="Bot Status", value="botstatus"),
                    create_choice(name="Increment Button", value="increment_button"),
                    create_choice(name="Bungie RSS Feed", value="rss"),
                ],
            ),
            create_option(
                name="channel",
                description="Which channel to the message should be in",
                option_type=7,
                required=True,
            ),
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _channel(self, ctx: SlashContext, channel_type, channel):
        if channel_type == "othergameroles":
            embed = embed_message(
                f"Other Game Roles", "Select options to add / delete the related roles"
            )

            components = [
                manage_components.create_actionrow(
                    manage_components.create_select(
                        options=[
                            manage_components.create_select_option(
                                emoji=self.client.get_emoji(game_values["emoji_id"]),
                                label=game_name,
                                value=f"{game_name}|{game_values['role_id']}",
                            )
                            # Options for games. Using the role id as value and emoji as emoji
                            for game_name, game_values in other_game_roles.items()
                        ],
                        custom_id="other_game_roles",
                        placeholder="Select options here",
                        min_values=1,
                        max_values=len(other_game_roles),
                    )
                ),
            ]

            await make_persistent_message(
                self.client,
                "otherGameRoles",
                ctx.guild.id,
                channel.id,
                components=components,
                message_embed=embed,
            )

        elif channel_type == "clanjoinrequest":
            components = [
                manage_components.create_actionrow(
                    manage_components.create_button(
                        custom_id="clan_join_request",
                        style=ButtonStyle.blue,
                        label="Click to Join the Clan",
                    ),
                ),
            ]

            await make_persistent_message(
                self.client,
                "clanJoinRequest",
                ctx.guild.id,
                channel.id,
                components=components,
                message_text="⁣",
            )

        elif channel_type == "registration":
            components = [
                manage_components.create_actionrow(
                    manage_components.create_button(
                        custom_id="registration",
                        style=ButtonStyle.blue,
                        label="Click to Connect your Destiny 2 Account",
                    ),
                ),
            ]

            await make_persistent_message(
                self.client,
                "registration",
                ctx.guild.id,
                channel.id,
                components=components,
                message_text="⁣",
            )

        elif channel_type == "increment_button":
            components = [
                manage_components.create_actionrow(
                    manage_components.create_button(
                        custom_id="increment_button", style=ButtonStyle.blue, label="0"
                    ),
                ),
            ]
            embed = embed_message(
                "Use the button to increase the count! Road to ram overflow!"
            )

            await make_persistent_message(
                self.client,
                "incrementButton",
                ctx.guild.id,
                channel.id,
                components=components,
                message_embed=embed,
            )

        elif channel_type == "steamjoincodes":
            await make_persistent_message(
                self.client,
                "steamJoinCodes",
                ctx.guild.id,
                channel.id,
                message_text="...",
            )

            # fill the empty message
            await steamJoinCodeMessage(self.client, ctx.guild)

        elif channel_type == "tournament":
            text = """
<:desc_title_left_b:768906489309822987><:desc_title_right_b:768906489729122344> **Welcome to the Tournament Channel!** <:desc_title_left_b:768906489309822987><:desc_title_mid_b:768906489103384657><:desc_title_mid_b:768906489103384657><:desc_title_right_b:768906489729122344>
⁣
On your command, I can start a private PvP tournament for all the masochist in the clan. You decide on details, such as rules, maps classes or anything else.
⁣
⁣
<:desc_title_left_b:768906489309822987><:desc_title_right_b:768906489729122344> **Tutorial** <:desc_title_left_b:768906489309822987> <:desc_title_mid_b:768906489103384657><:desc_title_mid_b:768906489103384657><:desc_title_right_b:768906489729122344>
:desc_circle_b: Create the tournament by using `/tournament insert`. This will make a new message appear in this channel, to join the tournament, simply react to it.
:desc_circle_b: Once everyone has signed up use `/tournament start` to start the tournament. I will generate a random bracket and assign player to games.
:desc_circle_b: Now you need to start a custom game with only the two chosen players in it and **finish it**. I will automatically detect the winner. Last man standing wins it all!
⁣
⁣"""

            await make_persistent_message(
                self.client,
                "tournamentChannel",
                ctx.guild.id,
                channel.id,
                message_text=text,
            )

        elif channel_type == "membercount":
            await make_persistent_message(
                self.client, "memberCount", ctx.guild.id, channel.id, no_message=True
            )

        elif channel_type == "boostercount":
            await make_persistent_message(
                self.client, "boosterCount", ctx.guild.id, channel.id, no_message=True
            )

        elif channel_type == "lfg":
            await make_persistent_message(
                self.client, "lfg", ctx.guild.id, channel.id, no_message=True
            )

            enter_emoji = ctx.bot.get_emoji(enter_emoji_id)
            circle_emoji = ctx.bot.get_emoji(circle_emoji_id)
            await channel.send(
                embed=embed_message(
                    "How to make an LFG post",
                    f"""
Hello fellow humans, and welcome to this easy, 465 steps, guide:
⁣
{str(circle_emoji)} **Step 1:**
First, head to <#{bot_spam_channel_id}>, or really any other channel (although you ~~might~~ will get yelled at for that)
⁣
{str(circle_emoji)} **Step 2:**
Then, use `/lfg insert` and follow the instructions to make an event. 
Due to timezones sucking and there being at least 16789 of them, you might not find your own timezone in the list. In that case please use UTC and an online converter
⁣
{str(circle_emoji)} **Step 3-464:**
Praise {ctx.bot.user.mention}!
⁣
{str(circle_emoji)} **Step 465:**
After you made the LFG post, or if you just want to join an existing post, use the fancy buttons to interact with the event
⁣
⁣
If you want to feel like an [expert](https://www.youtube.com/watch?v=BKorP55Aqvg), there are a bunch of additional commands you can use to interact with LFG events:
{str(enter_emoji)} `/lfg insert` - Create a new LFG event
{str(enter_emoji)} `/lfg edit` - Edit parts of an LFG event
{str(enter_emoji)} `/lfg delete` - Remove the LFG event
{str(enter_emoji)} `/lfg add` - Add a user to your own LFG event
{str(enter_emoji)} `/lfg kick` - Kick a user from your own LFG event
{str(enter_emoji)} `/lfg blacklist` - Blacklist a user from joining any of your own LFG events
⁣
⁣
Basically just type `/lfg` and look around. There are many other cool commands too, so maybe just type `/`""",
                    "If you find bugs or have feature requests, DM me",
                )
            )

        elif channel_type == "botstatus":
            embed = embed_message("Status: Last valid...")

            await make_persistent_message(
                self.client, "botStatus", 1, channel.id, message_embed=embed
            )

        elif channel_type == "lfgvoicecategory":
            await make_persistent_message(
                self.client,
                "lfgVoiceCategory",
                ctx.guild.id,
                channel.id,
                no_message=True,
            )

        elif channel_type == "rss":
            await make_persistent_message(
                self.client, "rss", ctx.guild.id, channel.id, no_message=True
            )

        await ctx.send(
            hidden=True, embed=embed_message(f"Success", f"I've done as you asked")
        )

    @cog_ext.cog_slash(
        name="updatedb",
        description="Forces a DB update with looks through ALL activities. Takes a long time",
        default_permission=False,
        permissions=permissions_kigstn_hali,
    )
    async def _update_db(self, ctx: SlashContext):
        print("Start updating DB...")
        message = await ctx.send(
            "Forcing DB update, this is gonna take a while. Will let you know once done"
        )

        # get all users the bot shares a guild with
        to_update = []
        for guild in ctx.bot.guilds:
            for member in guild.members:
                destiny_player = await DestinyPlayer.from_discord_id(member.id)

                # check if exists / already in list
                if destiny_player and destiny_player not in to_update:
                    to_update.append(destiny_player)

        # update all users in a gather for zooms
        await asyncio.gather(
            *[
                destiny_player.update_activity_db(entry_time=datetime.datetime.min)
                for destiny_player in to_update
            ]
        )

        await message.reply("Done with the DB update")

    # @cog_ext.cog_slash(
    #     name="test",
    #     guild_ids=GUILD_IDS
    # )
    # async def _test(self, ctx: SlashContext):
    #     select = manage_components.create_select(
    #         options=[
    #             manage_components.create_select_option("Option", value="option"),
    #         ],
    #         placeholder="Choose your option",
    #         min_values=1,
    #         max_values=1,
    #     )
    #     select_action = manage_components.create_actionrow(select)
    #     await ctx.send(content="select", components=[select_action])
    #
    #     button_ctx = await manage_components.wait_for_component(self.client, components=select_action)
    #     await button_ctx.edit_origin(content="edited", components=None)


def setup(client):
    client.add_cog(AdminCommands(client))
    client.add_cog(PersistentMessagesCommands(client))
