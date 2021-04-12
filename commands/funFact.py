import random

import aiohttp
import discord

from commands.base_command import BaseCommand


# has been slashified
class funFact(BaseCommand):
    def __init__(self):
        description = "Very fun fun facts just for fun"
        params = []
        super().__init__(description, params)
    
    async def handle(self, params, message, mentioned_user, client):
        url = "https://uselessfacts.jsph.pl/random.json?language=en"

        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as r:
                if r.status == 200:
                    text = (await r.json())["text"]

                    embed = discord.Embed(
                        title='Did you know?',
                        description=text
                    )

                    await message.channel.send(embed=embed)
