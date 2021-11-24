import asyncio
import itertools
import re
from copy import copy

from dis_snek.client import Snake
from dis_snek.models import Activity, ActivityType, Timestamp, TimestampStyles

from ElevatorBot.core.misc.persistentMessages import PersistentMessages
from ElevatorBot.misc.cache import descend_cache
from ElevatorBot.misc.helperFunctions import get_now_with_tz
from ElevatorBot.static.descendOnlyIds import descend_channels
from ElevatorBot.static.emojis import custom_emojis


async def update_discord_bot_status(client: Snake):
    """Update the Bot's status in an endless loop"""

    status_messages = [
        "Type '/' to see available commands",
        "Type '/register' to registration your Destiny 2 account",
        "DM me to contact staff",
        "↓ Psst! Did you know this person stinks",
        f"30th Anniversary releases in {Timestamp.fromtimestamp(1638900000).format(style=TimestampStyles.RelativeTime)}",
        f"Witch Queen releases in {Timestamp.fromtimestamp(1645552800).format(style=TimestampStyles.RelativeTime)}",
        "Rewrite complete",
        "To invite me to your own server, click on my user",
        "I can win the hard mode TicTacToe, can you?",
        "Presenting: Extra context! Right click a message or a user to be amazed",
        "I have been successfully snekified",
    ]

    for element in itertools.cycle(status_messages):
        await client.change_presence(activity=Activity.create(name=f"{custom_emojis.elevator_logo} {element}"))
        await asyncio.sleep(30)


async def update_events_status_message(event_name: str):
    """
    Update the status message in #admin-workboard showing background events
    Call with the event class name (CamelCase)
    """

    now = get_now_with_tz()
    correctly_formatted_event_name = " ".join(re.findall("[A-Z][^A-Z]*", event_name))
    correctly_formatted_event_time = Timestamp.fromdatetime(now).format(style=TimestampStyles.ShortDateTime)

    # get the message from cache
    if not descend_cache.message:
        persistent_messages = PersistentMessages(ctx=None, guild=descend_channels.guild, message_name="status")
        result = await persistent_messages.get()
        if not result:
            # when we have not set a message yet
            return

        channel = await descend_channels.guild.get_channel(result.channel_id)
        descend_cache.message = await channel.get_message(result.message_id)

    embed = copy(descend_cache.message.embeds[0])
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

    await descend_cache.message.edit(embeds=embed)
