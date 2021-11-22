import asyncio
import itertools

from dis_snek.client import Snake
from dis_snek.models import Activity, ActivityType, Timestamp, TimestampStyles

from ElevatorBot.static.emojis import custom_emojis


async def update_status(client: Snake):
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
