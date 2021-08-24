import asyncio
import itertools

import discord


async def update_status(client: discord.Client):
    """Update the Bot's status in an endless loop"""

    status_messages = [
        "Type '/' to see available commands",
        "Type '/registerdesc' to register your Destiny 2 account",
        "DM me to contact staff",
        "↓ Psst! Did you know this person stinks",
        "I head @Tom wants to be sherpa'd through GoS to finally get Divinity, but is too afraid to ask",
        "This message has been removed due to a request from @Feedy",
        "We all know who the best bot is",
        "Hint: Checkmarks are lame",
        "Hmm, maybe an actual versioning system would be about time",
        "Can I get vaccinated too? Technically I'm still a baby",
        "Chillin' in my Hot Tub right now 🍑💦",
        "I can win the hard mode TicTacToe, can you?",
        "Presenting: Extra context! Right click a message or a user to be amazed",
        "I am fluent in over six million forms of communication",
        "dis-snek > d.py",
        "Yehaw?",
    ]

    for element in itertools.cycle(status_messages):
        await client.change_presence(activity=discord.Game(name=element))
        await asyncio.sleep(30)
