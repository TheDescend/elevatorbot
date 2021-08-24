import asyncio
import io
import random

import aiohttp
import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.core.formating import embed_message
from ElevatorBot.core.miscFunctions import has_elevated_permissions
from ElevatorBot.core.poll import get_poll_object, create_poll_object
from ElevatorBot.core.roleLookup import assignRolesToUser, removeRolesFromUser
from ElevatorBot.core.slashCommandFunctions import get_user_obj
from ElevatorBot.static.globals import muted_role_id
from ElevatorBot.static.slashCommandConfig import permissions_socialist
from ElevatorBot.static.slashCommandOptions import options_user


class MiscCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="poll",
        base_description="Making polls easy",
        name="_insert",
        description="Create a poll",
        options=[
            create_option(
                name="name",
                description="The name the poll should have",
                option_type=3,
                required=True,
            ),
            create_option(
                name="description",
                description="The description the poll should have",
                option_type=3,
                required=True,
            ),
        ],
    )
    async def _poll_create(self, ctx: SlashContext, name: str, description: str):
        await create_poll_object(
            ctx=ctx,
            name=name,
            description=description,
            guild=ctx.guild,
            channel=ctx.channel,
        )

    @cog_ext.cog_subcommand(
        base="poll",
        base_description="Making polls easy",
        name="add",
        description="Add an option to a poll",
        options=[
            create_option(
                name="poll_id",
                description="The id of the poll",
                option_type=3,
                required=True,
            ),
            create_option(
                name="option",
                description="The name the option should have",
                option_type=3,
                required=True,
            ),
        ],
    )
    async def _poll_add(self, ctx: SlashContext, poll_id: str, option: str):
        poll = await get_poll_object(
            guild=ctx.guild,
            poll_id=poll_id,
        )
        if not poll:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Error",
                    f"Poll with `poll_id = {poll_id}` was not found in this guild",
                ),
            )
        else:
            # check if user is allowed
            if ctx.author == poll.author or await has_elevated_permissions(user=ctx.author, guild=ctx.guild, ctx=ctx):
                await poll.add_new_option(
                    ctx=ctx,
                    option=option,
                )

    @cog_ext.cog_subcommand(
        base="poll",
        base_description="Making polls easy",
        name="_delete",
        description="Remove an option from a poll",
        options=[
            create_option(
                name="poll_id",
                description="The id of the poll",
                option_type=3,
                required=True,
            ),
            create_option(
                name="option",
                description="The name of the option",
                option_type=3,
                required=True,
            ),
        ],
    )
    async def _poll_remove(self, ctx: SlashContext, poll_id: str, option: str):
        poll = await get_poll_object(
            guild=ctx.guild,
            poll_id=poll_id,
        )
        if not poll:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Error",
                    f"Poll with `poll_id = {poll_id}` was not found in this guild",
                ),
            )
        else:
            # check if user is allowed
            if ctx.author == poll.author or await has_elevated_permissions(user=ctx.author, guild=ctx.guild, ctx=ctx):
                await poll.remove_option(
                    ctx=ctx,
                    option=option,
                )

    @cog_ext.cog_subcommand(
        base="poll",
        base_description="Making polls easy",
        name="disable",
        description="Disable a poll",
        options=[
            create_option(
                name="poll_id",
                description="The id of the poll",
                option_type=3,
                required=True,
            ),
        ],
    )
    async def _poll_disable(self, ctx: SlashContext, poll_id: str):
        poll = await get_poll_object(
            guild=ctx.guild,
            poll_id=poll_id,
        )
        if not poll:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Error",
                    f"Poll with `poll_id = {poll_id}` was not found in this guild",
                ),
            )
        else:
            # check if user is allowed
            if ctx.author == poll.author or await has_elevated_permissions(user=ctx.author, guild=ctx.guild, ctx=ctx):
                await poll.disable(edit_ctx=ctx)

    @cog_ext.cog_slash(
        name="socialist",
        description="Spams #socialist",
        default_permission=False,
        permissions=permissions_socialist,
    )
    async def _socialist(self, ctx: SlashContext):
        await ctx.send("No 🙃")

    @cog_ext.cog_slash(name="boosters", description="Prints all premium subscribers")
    async def _boosters(self, ctx: SlashContext):
        sorted_premium_subscribers = sorted(ctx.guild.premium_subscribers, key=lambda m: m.premium_since, reverse=True)

        embed = embed_message(
            f"{ctx.guild.name} Nitro Boosters",
            ",\n".join(
                [
                    "**" + f"{m.display_name:<30}" + "** since: " + m.premium_since.strftime("%d/%m/%Y, %H:%M")
                    for m in sorted_premium_subscribers
                ]
            ),
        )

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="funfact", description="Very fun fun facts just for the funny fun of it")
    async def _funfact(self, ctx: SlashContext):
        await ctx.defer()

        url = "https://uselessfacts.jsph.pl/random.json?language=en"

        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as r:
                if r.status == 200:
                    text = (await r.json())["text"]
                else:
                    text = "Offline servers make it difficult to get fun facts :("

                await ctx.send(embed=embed_message("Did you know?", text.replace("`", "'")))

    @cog_ext.cog_slash(
        name="muteme",
        description="I wonder what this does...",
        options=[options_user()],
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
                async with session.get(
                    "https://media.istockphoto.com/videos/amazing-explosion-animation-with-text-congratulations-video-id1138902499?s=640x640"
                ) as resp:
                    if resp.status == 200:
                        data = io.BytesIO(await resp.read())
                        await author.send(file=discord.File(data, "congratulations.png"))

            await author.send(f"You won the jackpot! That's a timeout of **{timeout} minutes** for you, enjoy!")
        else:
            await author.send(f"You won a timout of **{timeout} minutes**, congratulations!!!")
            await asyncio.sleep(2)
            await author.send("Better luck next time if you were hunting for the jackpot")

        # add muted role
        print(f"Muting {author.display_name} for {timeout} minutes")
        await assignRolesToUser([muted_role_id], author, guild)

        # _delete muted role after time is over
        await asyncio.sleep(60 * timeout)

        # refresh user obj
        author = await guild.fetch_member(author.id)

        await removeRolesFromUser([muted_role_id], author, guild)
        await author.send("Sadly your victory is no more. Hope to see you back again soon!")

    @cog_ext.cog_slash(
        name="discordjoindate",
        description="Check your join date of this discord server",
        options=[options_user()],
    )
    async def _discordjoindate(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)
        await ctx.send(
            embed=embed_message(
                f"{user.display_name}'s Discord Join Date",
                f'You joined on `{user.joined_at.strftime("%d/%m/%Y, %H:%M")}`',
            )
        )


def setup(client):
    client.add_cog(MiscCommands(client))
