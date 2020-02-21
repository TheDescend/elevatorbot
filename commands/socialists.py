from commands.base_command  import BaseCommand

import discord
import random

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
        
        if socialist not in message.author.roles:
            await message.channel.send(f'Command reserved for {socialist.mention}s <:KKonaW:670369127445037057>')
            return
        
        if message.author.id == 216642123364171778:
            await forthesocialism.send(f'Any Socializers?')
        else:
            await forthesocialism.send(f'Any {socialist.mention}s?')