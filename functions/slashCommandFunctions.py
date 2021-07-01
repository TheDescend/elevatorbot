import datetime
from typing import Optional

import discord

from discord_slash import SlashContext

from database.database import lookupDestinyID, lookupSystem
from functions.formating import embed_message
from functions.miscFunctions import has_elevated_permissions
from functions.network import handleAndReturnToken


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


async def get_destinyID_and_system(ctx: SlashContext, discord_user) -> Optional[tuple[discord.Member, int, int]]:
    """" takes either a discord user_id or the user obj and return user obj, destinyID and system or None """

    var_type = type(discord_user)

    if var_type == int:
        user = ctx.bot.get_user(discord_user)
    elif var_type == discord.user.User or var_type == discord.member.Member:
        user = discord_user
    else:
        return None, None, None

    destinyID = await lookupDestinyID(user.id)
    system = await lookupSystem(destinyID)

    # check if user is registered and has a valid token
    if not (destinyID and system) or not (await handleAndReturnToken(user.id))["result"]:
        await ctx.send(hidden=True, embed=embed_message(
            f"Error",
            f"I either possess no information about {user.display_name} or their authentication is outdated. \nPlease `/registerdesc` to fix this issue'"
        ))
        return None, None, None

    return user, destinyID, system

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

