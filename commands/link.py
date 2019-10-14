from commands.base_command  import BaseCommand
from utils                  import get_emoji
from random                 import randint

from functions              import getNameToHashMapByClanid
from fuzzywuzzy             import fuzz
from fuzzywuzzy             import process
#from discord                import *

from functions import getPlayerRoles, getIDfromBungie

base_uri = 'https://discordapp.com/api/v7'
memberMap = getNameToHashMapByClanid(2784110)

class Link(BaseCommand): #TODO

    def __init__(self):
        # A quick description for the help message
        description = "registers you with the bot to check on roles and stuff, argument is your bungie.net profile or raid.report PC link\n if you don't know your raid.report link, try !rr"
        params = ["link"]
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        link = params[0]
        if 'bungie.net' in link:
            removeName = link[:link.rfind('/')]
            getTag = removeName[(removeName.rfind('/')+1):]
            destinyID = getIDfromBungie(int(getTag),3)
            print(destinyID)
        elif 'raid.report' in link:
            destinyID = int(link[(link.rfind('/')+1):])
            print(destinyID)
        else:
            await message.channel.send('please give either a bungie or a raid.report link')
            return
        
        await message.channel.send(f'Added user {message.author.mention} with id {destinyID}')
