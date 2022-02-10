import asyncio
import itertools
import re
from copy import copy

from dis_snek import Activity, Timestamp, TimestampStyles

from ElevatorBot.misc.cache import descend_cache
from Shared.functions.helperFunctions import get_now_with_tz
from version import __version__


async def update_discord_bot_status(client):
    """Update the Bots status in an endless loop"""

    status_messages = [
        f"Version: ElevatorBot@{__version__}",
        "Type `/` to see available commands",
        "Type `/register` to register your Destiny 2 account",
        "If you encounter a bug, please use `/bug`",
        "Also visit my website: `elevatorbot.ch`",
        "↓ Psst! Did you know this person stinks",
        f"Witch Queen releases {Timestamp.fromtimestamp(1645552800).format(style=TimestampStyles.RelativeTime)}",
        f"WQ raid releases {Timestamp.fromtimestamp(1646503200).format(style=TimestampStyles.RelativeTime)}",
        "To invite me to your own server, click on my profile",
        "I can win the hard mode TicTacToe, can you?",
        "@Feedy's removed message is now forever gone",
        "Presenting: Extra context! Right click a message or a user and be amazed",
        "What is dis? I have been snekified",
        "Now using Descend™ green",
        "Join the Descend discord: `discord.gg/descend`",
    ]

    for element in itertools.cycle(status_messages):
        await client.change_presence(activity=Activity.create(name=element))
        await asyncio.sleep(30)


async def update_events_status_message(event_name: str):
    """
    Update the status message in #admin-workboard showing background events
    Call with the event class name (CamelCase)
    """

    now = get_now_with_tz()
    correctly_formatted_event_name = " ".join(re.findall("[A-Z][^A-Z]*", event_name))
    correctly_formatted_event_time = f"{Timestamp.fromdatetime(now).format(style=TimestampStyles.ShortDateTime)} | {Timestamp.fromdatetime(now).format(style=TimestampStyles.RelativeTime)}"

    # get the message from cache
    if not descend_cache.status_message:
        return

    embed = copy(descend_cache.status_message.message.embeds[0])
    embed.timestamp = now

    # get all the fields from the embed and change the one we are looking for
    found = False
    for field in embed.fields:
        if field.name == correctly_formatted_event_name:
            field.value = correctly_formatted_event_time
            found = True
            break

    # field does not exist yet, add it
    if not found:
        embed.add_field(name=correctly_formatted_event_name, value=correctly_formatted_event_time, inline=True)

    await descend_cache.status_message.edit(embeds=embed)
