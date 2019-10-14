from commands.base_command  import BaseCommand
from utils                  import get_emoji
from random                 import randint
from functions              import getNameToHashMapByClanid
from fuzzywuzzy             import fuzz
from fuzzywuzzy             import process
#from discord                import *

base_uri = 'https://discordapp.com/api/v7'
# Your friendly example event
# Keep in mind that the command name will be derived from the class name
# but in lowercase

# So, a command class named Random will generate a 'random' command
class Userlist(BaseCommand):

    def __init__(self):
        # A quick description for the help message
        description = "Prints the userlist"
        # A list of parameters that the command will take as input
        # Parameters will be separated by spaces and fed to the 'params' 
        # argument in the handle() method
        # If no params are expected, leave this list empty or set it to None
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        # 'params' is a list that contains the parameters that the command 
        # expects to receive, t is guaranteed to have AT LEAST as many
        # parameters as specified in __init__
        # 'message' is the discord.py Message object for the command to handle
        # 'client' is the bot Client object

        memberMap = getNameToHashMapByClanid(2784110)

        server = message.guild
        if not server.unavailable:
            msg = ''
            memberList = server.members # <memberID, member obj>
            for memberObj in memberList:
                discordname = memberObj.nick or memberObj.name
                match = None
                maxProb = 0
                for ingameName in memberMap.keys():
                    prob = fuzz.ratio(discordname, ingameName)
                    #print('{} prob for '.format(prob) + discordname + ' = ' + ingameName)
                    if prob > maxProb and prob > 80:
                        maxProb = prob
                        match = ingameName
                if match:
                    msg += str(maxProb) + '% -> ' + discordname + ':' + memberMap[match] + "\n"
                else:
                    msg += 'Couldn\'t find ' + discordname + "\n"
                
            await message.channel.send(msg)
        #rolled = randint(lower_bound, upper_bound)
        #msg = get_emoji(":game_die:") + f" You rolled {rolled}!"

        #await client.send_message(message.channel, 'hi')
