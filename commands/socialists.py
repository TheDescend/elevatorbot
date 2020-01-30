from commands.base_command  import BaseCommand

import discord
import random

class socialists(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[depracted] Spam the socialists channel. USE AT YOUR OWN RISK"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received

    
    #msg = ''
    async def handle(self, params, message, client):
        #global msg
        channelID = 670573554315690007
        socialistID = 670579222468755458
        forthesocialism = client.get_channel(channelID)
        socialist = message.guild.get_role(socialistID)

        # if socialists.msg == '':
        #     for i in range(80):
        #         socialists.msg += socialist.mention + ' '
        # msg = socialists.msg
        
        if socialist not in message.author.roles:
            await message.channel.send(f'Command reserved for {socialist.mention}s <:KKonaW:670369127445037057>')
            return

        
        if message.author.id == 216642123364171778:
            await forthesocialism.send(f'Any Socializers?')
        # elif message.author.id == 367385031569702912:
        #     if random.randint(1, 3) == 1:
        #         await forthesocialism.send(f'Any {socialist.mention}s?')
        #     else:
        #         await forthesocialism.send(f'It\'s not very effective...')
        else:
            await forthesocialism.send(f'Any {socialist.mention}s?')
        #await message.delete()
        #
        #for k in range(20):
        #    await forthesocialism.send(msg)

        # with shelve.open('./shelves/socialistCount') as db:
        #     if str(message.author.id) in db:
        #         db[str(message.author.id)] += 1
        #     else:
        #         db[str(message.author.id)] = 1


class socialistsCount(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[depracted] Are you a real spammer though?"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        with shelve.open('./shelves/socialistCount') as db:
            if str(message.author.id) in db:
                await message.channel.send(f'You\'re a level {db[str(message.author.id)]} Socialists, contact {client.get_user(367385031569702912).mention} for more information>')
            else:
                await message.channel.send(f'Spam for the <:Communism:671806689829322783> first, then I will evaluate you')

