import asyncio
import itertools

from dis_snek.client import Snake
from dis_snek.models import Activity
from dis_snek.models import ActivityType

from ElevatorBot.static.emojis import elevator_logo_emoji_id


async def update_status(client: Snake):
    """Update the Bot's status in an endless loop"""

    status_messages = [
        "Type '/' to see available commands",
        "Type '/register' to registration your Destiny 2 account",
        "DM me to contact staff",
        "↓ Psst! Did you know this person stinks",
        "30th Anniversary releases in <t:1638900000:R>",
        "Witch Queen releases in <t:1645552800:R>",
        "Rewrite complete",
        "To invite me to your own server, type `/invite`",
        "I can win the hard mode TicTacToe, can you?",
        "Presenting: Extra context! Right click a message or a user to be amazed",
        "I have been successfully snekified",
    ]

    for element in itertools.cycle(status_messages):
        await client.change_presence(
            activity=Activity.create(
                name=f"<:elevatorLogo:{elevator_logo_emoji_id}> {element}", type=ActivityType.CUSTOM
            )
        )
        await asyncio.sleep(30)
