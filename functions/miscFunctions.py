import asyncio
import itertools

import discord
from discord_slash import SlashContext

from functions.database import getToken
from functions.formating import embed_message
from static.config import NOW_PLAYING
from static.globals import admin_role_id, dev_role_id, mod_role_id
from static.config import COMMAND_PREFIX


async def checkIfUserIsRegistered(user):
    if await getToken(user.id):
        return True
    else:
        embed = embed_message(
            "Error",
            "Please register with `!register` first (not via DMs)"
        )
        await user.send(embed=embed)
        return False


async def update_status(client):
    status_messages = [
        "DM me to contact Staff",
        "No more welcoming Neria please, she is no longer new",
        "I have been upgraded to v.2"
    ]

    if NOW_PLAYING:
        status_messages.append(NOW_PLAYING)

    print("Launching the Status Changer Loop", flush=True)
    for element in itertools.cycle(status_messages):
        await client.change_presence(activity=discord.Game(name=element))
        await asyncio.sleep(30)


# checks if user is allowed to use the command for other user.
async def hasMentionPermission(message, user, additionalUsers=[]):
    # if no other user is mentioned its ok anyways
    if user.id not in [message.author.id, *additionalUsers]:
        if not await hasAdminOrDevPermissions(message):
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to use this command for a different user here, please try again`'
            ))
            return False
    return True


# checks for admin or  dev permissions
async def hasAdminOrDevPermissions(message, send_message=True):
    admin = discord.utils.get(message.guild.roles, id=admin_role_id)
    dev = discord.utils.get(message.guild.roles, id=dev_role_id)
    mod = discord.utils.get(message.guild.roles, id=mod_role_id)

    # also checking for Kigstns id, to make that shit work on my local version of the bot
    if message.author.id == 238388130581839872:
        return True

    if admin not in message.author.roles and dev not in message.author.roles and mod not in message.author.roles:
        if send_message:
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to do that'
            ))
        return False
    return True


# todo swap old hasAdminOrDevPermissions stuff with this
async def has_elevated_permissions(user, guild, ctx: SlashContext = None):
    """ checks for admin or dev permissions, otherwise returns False. If ctx is given, return error message """
    admin = discord.utils.get(guild.roles, id=admin_role_id)
    dev = discord.utils.get(guild.roles, id=dev_role_id)
    mod = discord.utils.get(guild.roles, id=mod_role_id)

    # also checking for Kigstns id, to make that shit work on my local version of the bot
    if user.id == 238388130581839872:
        return True

    if admin not in user.roles and dev not in user.roles and mod not in user.roles:
        if ctx:
            await ctx.send('Error: You do not have permission do to this', hidden=True)
        return False
    return True


# should be called if incorrect params for command call where used
async def show_help(message, command, params):
    # work some magic that msg looks nice
    nice_looking_params = []
    for param in params:
        if param.startswith("*"):
            nice_looking_params.append(f"{param[:1]}<{param[1:]}>")
        else:
            nice_looking_params.append(f"<{param}>")

    await message.reply(embed=embed_message(
        "Incorrect Parameters",
        f"Correct usage is:\n`{COMMAND_PREFIX}{command} {' '.join(nice_looking_params)} *<user>`",
        "Info: The <user> parameter doesn't work for every command"
    ))


async def get_emoji(client, emoji_id):
    """ Return an emoji obj """

    return client.get_emoji(emoji_id)


def write_line(index, member, stat_text, stat):
    """ Write a line like charley does"""

    return f"{index}) **{member}** _({stat_text}: {stat})_"



