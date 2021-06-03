import asyncio
import random

from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

from functions.dataLoading import getNameAndCrossaveNameToHashMapByClanid, getProfile
from database.database import lookupDiscordID, lookupDestinyID, lookupSystem
from functions.formating import embed_message
from functions.network import getJSONfromURL, handleAndReturnToken
from functions.persistentMessages import make_persistent_message, steamJoinCodeMessage
from functions.roleLookup import assignRolesToUser, removeRolesFromUser
from static.config import CLANID, GUILD_IDS
from static.globals import other_game_roles, clan_join_request, muted_role_id
from static.slashCommandConfig import permissions_admin


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
        await ctx.send(hidden=True, embed=embed_message(
            "Please wait...",
            "The results will be here in a second"
        ))

        # get all clan members discordID
        memberlist = []
        for member in (await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"))["Response"][
            "results"]:
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
            if not (await handleAndReturnToken(discordID)):
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
                    "**These users have not yet accepted the rules**\n"
                    + tempstr
                )
                textstr = textstr[1900:]


    @cog_ext.cog_slash(
        name="getapikey",
        description="Get your API key",
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _getapikey(self, ctx: SlashContext):
        await ctx.send(hidden=True, embed=embed_message(
            "Your API Key",
            (await handleAndReturnToken(ctx.author.id))["result"]
        ))


    @cog_ext.cog_slash(
        name="getusermatching",
        description="Matches in-game and Discord names",
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _getUserMatching(self, ctx: SlashContext):
        await ctx.send(hidden=True, embed=embed_message(
            "Please wait...",
            "The results will be here in a second"
        ))

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
                    await ctx.channel.send(f'[ERROR] {steamname}/{crosssavename} with destinyID {userid} has discordID {discordID} but it is faulty')
            else:
                # user not found
                unsuccessfulMatches.append((steamname, crosssavename, userid))

        await ctx.channel.send('SUCCESSFUL MATCHES:')
        sortedSuccessfulMatches = sorted(successfulMatches, key=lambda pair: pair[2].lower())
        successfulMessage = ''
        for (steamname, crosssavename, username) in sortedSuccessfulMatches:
            successfulMessage += f'{username:<30} - {steamname} / {crosssavename}\n'

        if len(successfulMessage) < 2000:
            await ctx.channel.send(successfulMessage)
        else:
            remainingMessage = successfulMessage
            while curMessage := remainingMessage[:1900]:
                await ctx.channel.send(curMessage)
                remainingMessage = remainingMessage[1900:]
        await ctx.channel.send('FAILED MATCHES:')
        unsuccessfulMessage = ''
        for (steamname, crosssavename, userid) in unsuccessfulMatches:
            unsuccessfulMessage += f'{steamname} / {crosssavename} (Steam-ID {userid}) could not be found in Discord \n'

        if unsuccessfulMessage:
            await ctx.channel.send(unsuccessfulMessage)
        else:
            await ctx.channel.send('No unsuccessful matches <:PogU:670369128237760522>')


    @cog_ext.cog_slash(
        name="mute",
        description="Mutes specified user for specified time",
        options=[
            create_option(
                name="user",
                description="Which user to mute",
                option_type=6,
                required=True
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

        status = await ctx.send(embed=embed_message(
            "Success",
            f"Muted {user.mention} for {hours} hours\nI will edit this message once the time is over"
        ))

        await asyncio.sleep(hours*60*60)
        await removeRolesFromUser([muted_role_id], user, ctx.guild)

        await status.edit(embed=embed_message(
            "Success",
            f"{user.mention} is no longer muted"
        ))


    @cog_ext.cog_slash(
        name="reply",
        description="Send a message to whoever got tagged above",
        options=[
            create_option(
                name="message",
                description="What message to reply with",
                option_type=3,
                required=True
            ),
            create_option(
                name="user",
                description="Which user to reply to",
                option_type=6,
                required=False
            ),
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _reply(self, ctx: SlashContext, message: str, user=None):
        # gets the previous message
        previousMessage = (await ctx.channel.history(limit=1).flatten())[0]
        mentionedMembersInPreviousMessage = []

        # if previous message is posted by the bot and mentions at least 1 member
        if previousMessage.author == self.client.user and previousMessage.mentions:
            mentionedMembersInPreviousMessage = previousMessage.mentions

        # no one is tagged, someone is mentioned in the previous message
        if not user:
            if not mentionedMembersInPreviousMessage:
                await ctx.send('Make sure my message above mentions the user or fill them in as an argument')
                return

            else:
                if len(mentionedMembersInPreviousMessage) == 1:
                    # if the previous message mentions 1
                    if '@' in ctx.message.clean_content:
                        # but wait, the current message also mentions someone
                        await ctx.send('Not sure if you meant to ping someone or reply above')
                        return
                    # take the only mentioned member
                    user = mentionedMembersInPreviousMessage[0]

                else:
                    # if the previous message mentions more than 1
                    await ctx.send('Make sure my message above mentions the user or fill them in as an argument')
                    return

        assert(user is not None)

        await user.send(message)
        await ctx.send(f'{ctx.author.name} Answered\n`{message}`\nto {user.mention}')


    @cog_ext.cog_slash(
        name="rollreaction",
        description="Picks a random reactor from the post above",
        options=[
            create_option(
                name="draws",
                description="How many people to draw",
                option_type=4,
                required=True
            ),
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _rollreaction(self, ctx: SlashContext, draws: int):
        tmessage = (await ctx.channel.history(limit=1).flatten())[0]
        if not tmessage:
            await ctx.send(hidden=True, embed=embed_message(
                "Error",
                "Getting message failed"
            ))
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
            await ctx.send(hidden=True, embed=embed_message(
                "Error",
                "Not enough reactions found"
            ))
            return
        winners = [winner.mention for winner in random.sample(uniqueusers, draws)]
        await ctx.send(embed=embed_message(
            "Draw Result",
            f"Selected users {', '.join(winners)}"
        ))


    @cog_ext.cog_slash(
        name="getuserinfo",
        description="Get's database infos for the specified user",
        options=[
            create_option(
                name="discorduser",
                description="Look up a discord user",
                option_type=6,
                required=False
            ),
            create_option(
                name="destinyid",
                description="Look up a destinyID",
                option_type=3,
                required=False
            ),
            create_option(
                name="fuzzyname",
                description="If you know how the user is called",
                option_type=3,
                required=False
            ),
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _getuserinfo(self, ctx: SlashContext, discorduser=None, destinyid: str = None, fuzzyname: str = None):
        if (not (discorduser or destinyid or fuzzyname)) or (discorduser and destinyid) or (discorduser and fuzzyname) or (destinyid and fuzzyname) or (destinyid and discorduser and fuzzyname):
            await ctx.send(hidden=True, embed=embed_message(
                "Error",
                "Exactly one of the arguments must be used"
            ))
            return
        await ctx.defer()

        title = f"Database Infos"
        text = None

        # if disord info is given
        if destinyid:
            try:
                destinyid = int(destinyid)
            except ValueError:
                await ctx.send(embed=embed_message(
                    "Error",
                    f"DestinyID must be a number"
                ))
                return

            destinyID = destinyid
            discordID = await lookupDiscordID(destinyID)
            mentioned_user = self.client.get_user(discordID)
            if not mentioned_user:
                await ctx.send(embed=embed_message(
                    "Error",
                    f"I don't know a user with the destinyID `{destinyID}`"
                ))
                return
            title = f'Database Infos for {mentioned_user.display_name}'
            text = f"""DiscordID - `{discordID}` \nDestinyID: `{destinyID}` \nSystem - `{await lookupSystem(destinyID)}` \nSteamName - `{(await getProfile(destinyID, 100))["profile"]["data"]["userInfo"]["displayName"]}` \nHasToken - `{bool((await handleAndReturnToken(discordID))["result"])}`"""

        # if destiny id is given
        elif discorduser:
            mentioned_user = discorduser
            discordID = mentioned_user.id
            destinyID = await lookupDestinyID(discordID)
            title = f'Database Infos for {mentioned_user.display_name}'
            text = f"""DiscordID - `{discordID}` \nDestinyID: `{destinyID}` \nSystem - `{await lookupSystem(destinyID)}` \nSteamName - `{(await getProfile(destinyID, 100))["profile"]["data"]["userInfo"]["displayName"] if destinyID else None}` \nHasToken - `{bool((await handleAndReturnToken(discordID))["result"])}`"""

        embed = embed_message(
            title,
            text if text else f'Possible matches for {fuzzyname}'
        )

        # if fuzzy name is given
        if fuzzyname:
            clansearch = []
            returnjson = await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members?nameSearch={fuzzyname}")
            clansearch.append(returnjson)

            for result in clansearch:
                resp = result['Response']
                if not resp['results']:
                    await ctx.send(embed=embed_message(
                        f'Error',
                        f"No matches found for `{fuzzyname}`"
                    ))
                    return

                i = 0
                for guy in resp['results']:
                    i += 1
                    steam_name = guy['destinyUserInfo']['LastSeenDisplayName']
                    bungie_name = guy['bungieNetUserInfo']['displayName']
                    destinyID = int(guy['destinyUserInfo']['membershipId'])
                    discordID = await lookupDiscordID(destinyID)
                    embed.add_field(name=f"Option {i}", value=f"Discord - <@{discordID}>\nSteamName - {steam_name}\nBungieName - {bungie_name}", inline=False)

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
                    create_choice(
                        name="Clan Join Request",
                        value="clanjoinrequest"
                    ),
                    create_choice(
                        name="Other Game Roles",
                        value="othergameroles"
                    ),
                    create_choice(
                        name="Steam Join Codes",
                        value="steamjoincodes"
                    ),
                    create_choice(
                        name="Tournament",
                        value="tournament"
                    ),
                    create_choice(
                        name="Member Count",
                        value="membercount"
                    ),
                    create_choice(
                        name="Booster Count",
                        value="boostercount"
                    ),
                    create_choice(
                        name="Looking For Group",
                        value="lfg"
                    ),
                ],
            ),
            create_option(
                 name="channel",
                 description="Which channel to the message should be in",
                 option_type=7,
                 required=True
            )
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _channel(self, ctx: SlashContext, channel_type, channel):
        if channel_type == "othergameroles":
            embed = embed_message(
                f'Other Game Roles',
                f'React to add / remove other game roles'
            )

            # react with those please thanks
            emoji_id_list = []
            for emoji_id, _ in other_game_roles:
                emoji_id_list.append(emoji_id)

            await make_persistent_message(self.client, "otherGameRoles", ctx.guild.id, channel.id, reaction_id_list=emoji_id_list, message_embed=embed)

            await ctx.send(hidden=True, embed=embed_message(
                f"Success",
                f"I've done as you asked"
            ))


        elif channel_type == "clanjoinrequest":
            embed = embed_message(
                f'Clan Application',
                f'React if you want to join the clan'
            )

            await make_persistent_message(self.client, "clanJoinRequest", ctx.guild.id, channel.id,
                                          reaction_id_list=clan_join_request, message_embed=embed)

            await ctx.send(hidden=True, embed=embed_message(
                f"Success",
                f"I've done as you asked"
            ))


        elif channel_type == "steamjoincodes":
            await make_persistent_message(self.client, "steamJoinCodes", ctx.guild.id, channel.id, message_text="...")

            # fill the empty message
            await steamJoinCodeMessage(self.client, ctx.guild)

            await ctx.send(hidden=True, embed=embed_message(
                f"Success",
                f"I've done as you asked"
            ))


        elif channel_type == "tournament":
            text = """
<:desc_title_left_b:768906489309822987><:desc_title_right_b:768906489729122344> **Welcome to the Tournament Channel!** <:desc_title_left_b:768906489309822987><:desc_title_mid_b:768906489103384657><:desc_title_mid_b:768906489103384657><:desc_title_right_b:768906489729122344>
⁣
On your command, I can start a private PvP tournament for all the masochist in the clan. You decide on details, such as rules, maps classes or anything else.
⁣
⁣
<:desc_title_left_b:768906489309822987><:desc_title_right_b:768906489729122344> **Tutorial** <:desc_title_left_b:768906489309822987> <:desc_title_mid_b:768906489103384657><:desc_title_mid_b:768906489103384657><:desc_title_right_b:768906489729122344>
:desc_circle_b: Create the tournament by using `/tournament create`. This will make a new message appear in this channel, to join the tournament, simply react to it.
:desc_circle_b: Once everyone has signed up use `/tournament start` to start the tournament. I will generate a random bracket and assign player to games.
:desc_circle_b: Now you need to start a custom game with only the two chosen players in it and **finish it**. I will automatically detect the winner. Last man standing wins it all!
⁣
⁣"""

            await make_persistent_message(self.client, "tournamentChannel", ctx.guild.id, channel.id, message_text=text)

            await ctx.send(hidden=True, embed=embed_message(
                f"Success",
                f"I've done as you asked"
            ))


        elif channel_type == "membercount":
            await make_persistent_message(self.client, "memberCount", ctx.guild.id, channel.id, no_message=True)
            await ctx.send(hidden=True, embed=embed_message(
                f"Success",
                f"I've done as you asked"
            ))


        elif channel_type == "boostercount":
            await make_persistent_message(self.client, "boosterCount", ctx.guild.id, channel.id, no_message=True)
            await ctx.send(hidden=True, embed=embed_message(
                f"Success",
                f"I've done as you asked"
            ))

        elif channel_type == "lfg":
            await make_persistent_message(self.client, "lfg", ctx.guild.id, channel.id, no_message=True)
            await ctx.send(hidden=True, embed=embed_message(
                f"Success",
                f"I've done as you asked"
            ))


def setup(client):
    client.add_cog(AdminCommands(client))
    client.add_cog(PersistentMessagesCommands(client))
