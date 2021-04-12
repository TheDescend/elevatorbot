from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from functions.formating import embed_message
from functions.persistentMessages import make_persistent_message, steamJoinCodeMessage
from static.config import GUILD_IDS
from static.globals import among_us_emoji_id, barotrauma_emoji_id, gta_emoji_id, valorant_emoji_id, lol_emoji_id, \
    eft_emoji_id, destiny_emoji_id, other_game_roles, clan_join_request


class AdminCommands(commands.Cog):
    def __init__(self, client):
        self.client = client


class PersistenMessagesCommands(commands.Cog):
    def __init__(self, client):
        self.client = client


    @cog_ext.cog_subcommand(
        base="persistentmessage",
        base_description="[Admin] Make new / replace old persistent messages ",
        name="botstatus",
        description="Displays various bot status messages",
        options=[
            create_option(
                name="channel",
                description="Which channel to the message should be in",
                option_type=7,
                required=True
            )
        ]
    )
    async def _botstatus(self, ctx: SlashContext, channel):
        embed = embed_message(
            "Status: Last valid..."
        )
        await make_persistent_message(self.client, "botStatus", ctx.guild.id, channel.id, message_embed=embed)

        await ctx.send("Done", hidden=True)


    @cog_ext.cog_subcommand(
        base="persistentmessage",
        base_description="[Admin] Make new / replace old persistent messages ",
        name="othergameroles",
        description="Displays other games users can react to to get a role",
        options=[
            create_option(
                name="channel",
                description="Which channel to the message should be in",
                option_type=7,
                required=True
            )
        ]
    )
    async def _othergameroles(self, ctx: SlashContext, channel):
        embed = embed_message(
            f'Other Game Roles',
            f'React to add / remove other game roles'
        )

        # react with those please thanks
        emoji_id_list = []
        for emoji_id, _ in other_game_roles:
            emoji_id_list.append(emoji_id)

        await make_persistent_message(self.client, "otherGameRoles", ctx.guild.id, channel.id, reaction_id_list=emoji_id_list, message_embed=embed)

        await ctx.send("Done", hidden=True)


    @cog_ext.cog_subcommand(
        base="persistentmessage",
        base_description="[Admin] Make new / replace old persistent messages ",
        name="clanjoinrequest",
        description="Allows users to invite themself to the Destiny 2 clan",
        options=[
            create_option(
                name="channel",
                description="Which channel to the message should be in",
                option_type=7,
                required=True
            )
        ]
    )
    async def _clanjoinrequest(self, ctx: SlashContext, channel):
        embed = embed_message(
            f'Clan Application',
            f'React if you want to join the clan'
        )

        await make_persistent_message(self.client, "clanJoinRequest", ctx.guild.id, channel.id, reaction_id_list=clan_join_request, message_embed=embed)

        await ctx.send("Done", hidden=True)


    @cog_ext.cog_subcommand(
        base="persistentmessage",
        base_description="[Admin] Make new / replace old persistent messages ",
        name="steamjoincodes",
        description="Displays steam join codes users can use to join on people",
        options=[
            create_option(
                name="channel",
                description="Which channel to the message should be in",
                option_type=7,
                required=True
            )
        ]
    )
    async def _steamjoincodes(self, ctx: SlashContext, channel):
        await make_persistent_message(self.client, "steamJoinCodes", ctx.guild.id, channel.id, message_text="...")

        # fill the empty message
        await steamJoinCodeMessage(self.client, ctx.guild)

        await ctx.send("Done", hidden=True)


def setup(client):
    client.add_cog(AdminCommands(client))
    # todo enable when persmissions are implemented
    # client.add_cog(PersistenMessagesCommands(client))
