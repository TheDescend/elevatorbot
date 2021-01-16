import asyncio
import itertools

import discord

from functions.database import getToken
from functions.formating import embed_message
from static.config import NOW_PLAYING
from static.globals import admin_role_id, dev_role_id, mod_role_id


async def checkIfUserIsRegistered(user):
    if getToken(user.id):
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
        "#MakeHäbidöpfelMascot",
        "!startCounting",
        "!muteMe",
        "Send me funny memes please",
    ]

    if NOW_PLAYING:
        status_messages.append(NOW_PLAYING)

    print("Launching the Status Changer Loop", flush=True)
    for element in itertools.cycle(status_messages):
        await client.change_presence(activity=discord.Game(name=element))
        await asyncio.sleep(30)


# checks if user is allowed to use the command for other user.
async def hasMentionPermission(message, user):
    # if no other user is mentioned its ok anyways
    if user.id is not message.author.id:
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