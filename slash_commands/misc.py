import asyncio
import io
import random

import aiohttp
import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from functions.formating import embed_message
from functions.roleLookup import assignRolesToUser, removeRolesFromUser
from functions.slashCommandFunctions import get_user_obj
from static.config import GUILD_IDS
from static.globals import muted_role_id


class MiscCommands(commands.Cog):
    def __init__(self, client):
        self.client = client


    @cog_ext.cog_slash(
        name="boosters",
        description="Prints all premium subscribers"
    )
    async def _boosters(self, ctx: SlashContext):
        sorted_premium_subscribers = sorted(ctx.guild.premium_subscribers, key=lambda m:m.premium_since.strftime('%d/%m/%Y, %H:%M'), reverse=True)

        embed = embed_message(
            f"{ctx.guild.name} Nitro Boosters",
            ",\n".join(['**' + f"{m.display_name:<30}" + "** since: " + m.premium_since.strftime('%d/%m/%Y, %H:%M') for m in sorted_premium_subscribers])
        )

        await ctx.send(embed=embed)


    # @cog_ext.cog_slash(
    #     name="documentation",
    #     description="Links the bots' documentation"
    # )
    # async def _documentation(self, ctx: SlashContext):
    #     await ctx.send('Check out https://github.com/LukasSchmid97/destinyBloodoakStats/blob/master/README.md')


    @cog_ext.cog_slash(
        name="funfact",
        description="Very fun fun facts just for the funny fun of it"
    )
    async def _funfact(self, ctx: SlashContext):
        await ctx.defer()

        url = "https://uselessfacts.jsph.pl/random.json?language=en"

        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as r:
                if r.status == 200:
                    text = (await r.json())["text"]
                else:
                    text = "Offline servers make it difficult to get fun facts :("

                await ctx.send(embed=embed_message(
                    'Did you know?',
                    text
                ))


    @cog_ext.cog_slash(
        name="muteme",
        description="I wonder what this does...",
        options=[
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            )
        ]
    )
    async def _muteme(self, ctx: SlashContext, **kwargs):
        await ctx.defer()

        user = await get_user_obj(ctx, kwargs)

        author = ctx.author
        guild = ctx.guild

        if author.id is not user.id:
            await ctx.send("I saw what you did there, that doesn't work here mate")
        else:
            await ctx.send("If you insist...")

        await author.send("Introducing a new feature: **gambling!**")
        await asyncio.sleep(1)
        await author.send("Let me roll the dice for you, I can't wait to see if you win the jackpot")
        await asyncio.sleep(2)
        await author.send("_Rolling dice..._")
        await asyncio.sleep(5)
        timeout = random.choice([5, 10, 15, 30, 45, 60, 120])
        if timeout == 120:
            await author.send("**__!!! CONGRATULATIONS !!!__**")
            async with aiohttp.ClientSession() as session:
                async with session.get("https://media.istockphoto.com/videos/amazing-explosion-animation-with-text-congratulations-video-id1138902499?s=640x640") as resp:
                    if resp.status == 200:
                        data = io.BytesIO(await resp.read())
                        await author.send(file=discord.File(data, 'congratulations.png'))

            await author.send(f"You won the jackpot! That's a timeout of **{timeout} minutes** for you, enjoy!")
        else:
            await author.send(f"You won a timout of **{timeout} minutes**, congratulations!!!")
            await asyncio.sleep(2)
            await author.send("Better luck next time if you were hunting for the jackpot")

        # add muted role
        print(f"Muting {author.display_name} for {timeout} minutes")
        await assignRolesToUser([muted_role_id], author, guild)

        # remove muted role after time is over
        await asyncio.sleep(60 * timeout)
        await removeRolesFromUser([muted_role_id], author, guild)
        await author.send("Sadly your victory is no more. Hope to see you back again soon!")


    @cog_ext.cog_slash(
        name="saymyname",
        description="Say your name"
    )
    async def _boosters(self, ctx: SlashContext):
        await ctx.send(ctx.author.display_name, tts=True)


    @cog_ext.cog_slash(
        name="discordjoindate",
        description="Check your join date of this discord server",
        options=[
            create_option(
                name="user",
                description="The name of the user you want to look up",
                option_type=6,
                required=False
            )
        ]
    )
    async def _discordjoindate(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)
        await ctx.send(embed=embed_message(
            f"{user.display_name}'s Discord Join Date",
            f'You joined on `{user.joined_at.strftime("%d/%m/%Y, %H:%M")}`'
        ))


def setup(client):
    client.add_cog(MiscCommands(client))
