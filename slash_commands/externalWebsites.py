from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from functions.database import lookupDestinyID, lookupSystem
from functions.formating import embed_message
from functions.slashCommandFunctions import get_user_obj, get_destinyID_and_system
from static.config import GUILD_IDS


class ExternalWebsitesCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.rrsystem = {
            1: 'xb',
            2: 'ps',
            3: 'pc'
        }

    @cog_ext.cog_slash(
        name="sr",
        description="Gets your personal soloreport link",
        options=[
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            )
        ]
    )
    async def _sr(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)

        _, destinyID, system = await get_destinyID_and_system(ctx, user)

        if destinyID:
            await ctx.send(embed=embed_message(
                'Solo Report',
                f'https://elevatorbot.ch/soloreport/{system}/{destinyID}'
            ))


    @cog_ext.cog_slash(
        name="rr",
        description="Gets your personal raid.report link",
        options=[
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            )
        ]
    )
    async def _rr(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)

        _, destinyID, system = await get_destinyID_and_system(ctx, user)

        if destinyID:
            await ctx.send(embed=embed_message(
                'Raid Report',
                f'https://raid.report/{self.rrsystem[system]}/{destinyID}'
            ))


    @cog_ext.cog_slash(
        name="dr",
        description="Gets your personal dungeon.report link",
        options=[
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            )
        ]
    )
    async def _dr(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)

        _, destinyID, system = await get_destinyID_and_system(ctx, user)

        if destinyID:
            await ctx.send(embed=embed_message(
                'Dungeon Report',
                f'https://dungeon.report/{self.rrsystem[system]}/{destinyID}'
            ))


    @cog_ext.cog_slash(
        name="gr",
        description="Gets your personal grandmaster.report link",
        options=[
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            )
        ]
    )
    async def _gr(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)

        _, destinyID, system = await get_destinyID_and_system(ctx, user)

        if destinyID:
            await ctx.send(embed=embed_message(
                'Grandmaster Report',
                f'https://grandmaster.report/user/{system}/{destinyID}'
            ))


    @cog_ext.cog_slash(
        name="nr",
        description="Gets your personal nightfall.report link",
        options=[
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            )
        ]
    )
    async def _nr(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)

        _, destinyID, system = await get_destinyID_and_system(ctx, user)

        if destinyID:
            await ctx.send(embed=embed_message(
                'Nightfall Report',
                f'https://nightfall.report/guardian/{system}/{destinyID}'
            ))


    @cog_ext.cog_slash(
        name="tr",
        description="Gets your personal destinytrialsreport link",
        options=[
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            )
        ]
    )
    async def _tr(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)

        _, destinyID, system = await get_destinyID_and_system(ctx, user)

        if destinyID:
            await ctx.send(embed=embed_message(
                'Trials Report',
                f'https://destinytrialsreport.com/report/{system}/{destinyID}'
            ))


def setup(client):
    client.add_cog(ExternalWebsitesCommands(client))
