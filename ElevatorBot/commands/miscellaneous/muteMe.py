import asyncio
import datetime
import io
import random

import aiohttp
from dis_snek import File
from dis_snek.models import InteractionContext, Member, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.helperFunctions import get_now_with_tz
from settings import COMMAND_GUILD_SCOPE

# =============
# Descend Only!
# =============


class MuteMe(BaseScale):
    @slash_command(name="mute_me", description="I wonder what this does...", scopes=COMMAND_GUILD_SCOPE)
    @default_user_option()
    async def mute_me(self, ctx: InteractionContext, user: Member = None):

        # no mentioning others here smiley face
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
                        image = File(file_name="congratulations.png", file=data)
                        await ctx.author.send(file=image)

            await ctx.author.send(f"You won the jackpot! That's a timeout of **{timeout} minutes** for you, enjoy!")
        else:
            await ctx.author.send(f"You won a timout of **{timeout} minutes**, congratulations!!!")
            await asyncio.sleep(2)
            await ctx.author.send("Better luck next time if you were hunting for the jackpot")

        # time them out
        await ctx.author.timeout(
            communication_disabled_until=get_now_with_tz() + datetime.timedelta(minutes=timeout),
            reason=f"/muteme by {ctx.author}",
        )

        # inform user once timeout is over
        await asyncio.sleep(60 * timeout)
        await ctx.author.send(
            "Sadly your victory is no more and you are no longer timed out. Hope to see you back again soon!"
        )


def setup(client):
    MuteMe(client)
