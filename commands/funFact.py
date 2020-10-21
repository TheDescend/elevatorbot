from commands.base_command  import BaseCommand

import aiohttp
import discord
import random

class funFact(BaseCommand):
    def __init__(self):
        description = "Very fun fun facts just for fun"
        params = []
        super().__init__(description, params)
    
    async def handle(self, params, message, client):
        text = f"Sorry, out of fun facts for now"
        
        r = random.random()
        if r > 0.95:
            text = f"Don't let <@206878830017773568> see you using this command <:monkaO:670672093070753816>"
        else:
            url = "https://uselessfacts.jsph.pl/random.json?language=en"

            async with aiohttp.ClientSession() as session:
                async with session.get(url=url) as r:
                    if r.status == 200:
                        text = (await r.json())["text"]
            
                        embed = discord.Embed(
                            title = 'Did you know?',
                            description = text
                        )

                        await message.channel.send(embed=embed)