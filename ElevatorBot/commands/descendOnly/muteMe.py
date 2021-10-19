import asyncio
import io
import random

import aiohttp
import discord
from discord.ext.commands import Cog
from discord_slash import cog_ext
from discord_slash import SlashContext

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.misc.discordShortcutFunctions import assign_roles_to_member
from ElevatorBot.misc.discordShortcutFunctions import remove_roles_from_member
from ElevatorBot.static.descendOnlyIds import descend_muted_role_id


class MuteMe(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="muteme",
        description="I wonder what this does...",
        options=[default_user_option()],
    )
    async def _mute_me(self, ctx: SlashContext, user: discord.Member = None):
        """I wonder what this does..."""

        # no mentioning others here smileyface
        if user:
            await ctx.send("I saw what you did there, that doesn't work here mate")
        else:
            await ctx.send("If you insist...")

        # send a novel and calculate how long to mute
        await ctx.author.send("Introducing a new feature: **gambling!**")
        await asyncio.sleep(1)
        await ctx.author.send("Let me roll the dice for you, I can't wait to see if you win the jackpot")
        await asyncio.sleep(2)
        await ctx.author.send("_Rolling dice..._")
        await asyncio.sleep(5)
        timeout = random.choice([5, 10, 15, 30, 45, 60, 120])
        if timeout == 120:
            await ctx.author.send("**__!!! CONGRATULATIONS !!!__**")
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://media.istockphoto.com/videos/amazing-explosion-animation-with-text-congratulations-video-id1138902499?s=640x640"
                ) as resp:
                    if resp.status == 200:
                        data = io.BytesIO(await resp.read())
                        await ctx.author.send(file=discord.File(data, "congratulations.png"))

            await ctx.author.send(f"You won the jackpot! That's a timeout of **{timeout} minutes** for you, enjoy!")
        else:
            await ctx.author.send(f"You won a timout of **{timeout} minutes**, congratulations!!!")
            await asyncio.sleep(2)
            await ctx.author.send("Better luck next time if you were hunting for the jackpot")

        # add muted role
        await assign_roles_to_member(ctx.author, descend_muted_role_id, reason=f"/muteme by {ctx.author}")

        # delete muted role after time is over
        await asyncio.sleep(60 * timeout)

        await remove_roles_from_member(user, descend_muted_role_id, reason=f"/muteme by {ctx.author}")
        await ctx.author.send(
            "Sadly your victory is no more and you are no longer muted. Hope to see you back again soon!"
        )


def setup(client):
    client.add_cog(MuteMe(client))
