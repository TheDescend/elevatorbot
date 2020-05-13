from commands.base_command  import BaseCommand

import discord
import random
import os
import json
from random import random

class socialists(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[depracted] Spam the socialists channel. USE AT YOUR OWN RISK"
        params = []
        super().__init__(description, params)
    
    async def handle(self, params, message, client):
        channelID = 670573554315690007
        socialistID = 670579222468755458
        
        forthesocialism = client.get_channel(channelID)
        socialist = message.guild.get_role(socialistID)


        with open('sc.json', 'r') as fp:
            counts = json.load(fp)
        
        if str(message.author.id) in counts:
            counts[str(message.author.id)] = 1 + counts[str(message.author.id)]
        else:
            counts[str(message.author.id)] = 1

        with open('sc.json', 'w') as fp:
                json.dump(counts, fp)

        if socialist not in message.author.roles:
            await message.channel.send(f'Command reserved for {socialist.mention}s <:KKonaW:670369127445037057>')
            return
        
        if message.author.id == 216642123364171778:
            await forthesocialism.send(f'Any Socializers?')
        else:
            await forthesocialism.send(f'Any {socialist.mention}s?')

# class socialistss(BaseCommand):
#     def __init__(self):
#         # A quick description for the help message
#         description = "Prints the amount of socialist commands you've done"
#         params = []
#         super().__init__(description, params)
    
#     async def handle(self, params, message, client):
#         if random() > 0.9:
#             message.channel.send(f'{caller} has 69 socialists')

#         if not os.path.exists('sc.json'):
#             with open('sc.json', 'w+') as fp:
#                 json.dump({}, fp)
#         with open('sc.json', 'r') as fp:
#             counts = json.load(fp)
#         caller = message.author.nick or message.author.name
        
#         if counts[str(message.author.id)] == 420:
#             await message.channel.send(f'{caller} has 419 socialists')
#         await message.channel.send(f'{caller} has {counts[str(message.author.id)]} socialists')