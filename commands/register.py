from commands.base_command  import BaseCommand
from utils                  import get_emoji
from random                 import randint

from functions              import getNameToHashMapByClanid
from fuzzywuzzy             import fuzz
from fuzzywuzzy             import process
#from discord                import *

from functions import getPlayerRoles

base_uri = 'https://discordapp.com/api/v7'
memberMap = getNameToHashMapByClanid(2784110)

class RegisterWithBungie(BaseCommand): #TODO

    def __init__(self):
        # A quick description for the help message
        description = "registers you with the bot to check on roles and stuff"
        params = ["username"]
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):

        username = str(params[0])
        if username == '0':
            username = message.author.display_name
        userid = None
        maxProb = 0
        for ingameName in memberMap.keys():
            prob = fuzz.ratio(username, ingameName)
            #print('{} prob for '.format(prob) + username + ' = ' + ingameName)
            if prob > maxProb and prob > 60:
                maxProb = prob
                userid = memberMap[ingameName]
        if userid:
            async with message.channel.typing():
                await message.channel.send(str(getPlayerRoles(userid)))
        else:
            await message.channel.send('Please be more specific')
        

        
