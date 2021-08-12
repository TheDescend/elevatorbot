import datetime

import discord
from discord_slash import SlashContext

from functions.formating import embed_message
from functions.miscFunctions import has_elevated_permissions


async def get_user_obj(ctx: SlashContext, kwargs: dict = None) -> discord.Member:
    """ Returns the user object of the mentioned user in the kwargs, if emtpy, return author """

    if "user" in kwargs:
        return kwargs["user"]
    return ctx.author


async def get_user_obj_admin(ctx: SlashContext, kwargs: dict = None, allowed_users: list = None):
    """ Shadows get_user_obj(), but only returns if user has elevated permssions (admin / mod) or arg wasn't used or author is in the allowed_users list of int ids"""

    if allowed_users is None:
        allowed_users = []

    user = await get_user_obj(ctx, kwargs)

    if await has_elevated_permissions(ctx.author, ctx.guild) or user == ctx.author or ctx.author.id in allowed_users:
        return user

    await ctx.send(hidden=True, embed=embed_message(
        f"Error",
        f"You do not have permission do to this"
    ))
    return


async def verify_time_input(ctx, input):
    """ Verifies that the user input is a valid time and returns the datetime obj. Else returns False """

    # make sure the times are valid
    try:
        return datetime.datetime.strptime(input, "%d/%m/%y")
    except ValueError:
        await ctx.send(hidden=True, embed=embed_message(
            f"Error",
            f"The time parameters must be in this format - `DD/MM/YY`"
        ))
        return False

