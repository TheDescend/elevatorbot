import asyncio
import itertools

import discord

from functions.database import getToken
from functions.formating import embed_message
from static.config import NOW_PLAYING


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
        "Bounties are the endgame",
        "#MakeHäbidöpfelMascot"
    ]

    if NOW_PLAYING:
        status_messages.append(NOW_PLAYING)

    print("Launching the Status Changer Loop", flush=True)
    for element in itertools.cycle(status_messages):
        await client.change_presence(activity=discord.Game(name=element))
        await asyncio.sleep(30)
