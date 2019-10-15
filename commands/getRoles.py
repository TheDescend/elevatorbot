from commands.base_command  import BaseCommand
from utils                  import get_emoji
from random                 import randint

from functions              import getNameToHashMapByClanid
from fuzzywuzzy             import fuzz
from fuzzywuzzy             import process
#from discord                import *

from functions import getPlayerRoles
import discord

base_uri = 'https://discordapp.com/api/v7'
bungie_base = ''
bungie_getMembershipId_by_bungieName = '/Destiny/[MembershipType]/Stats/GetMembershipIdByDisplayName/[DisplayName]'
memberMap = getNameToHashMapByClanid(2784110)

#TODO function finduser in functions with all this stuff in it
#TODO check against all available names in the bungie-thiny gotten from each id in the clan

class getRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "gets the roles of a bloodoakplayer by ingameName"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        username = message.author.display_name
        if len(params) == 1:
            username = str(params[0])
        maxName = None
        maxProb = 50
        for ingameName in memberMap.keys():
            #prob = fuzz.ratio(username, ingameName)
            uqprob = fuzz.UQRatio(username, ingameName)
            #uwprob = fuzz.UWRatio(username, ingameName)
            if uqprob > maxProb:
                #strng = '{} prob, '.format(prob) + " " + '{} prob, '.format(uqprob) + '{} prob '.format(uwprob)+ username + ' = ' + ingameName
                #await message.channel.send(strng)
                maxProb = uqprob
                maxName = ingameName
        if not maxName:
            await message.channel.send(f'User {username} not found in BO I')
            return
        steamName = maxName

        maxUser = None
        maxProb = 50
        uqprob = 0
        for discordUser in message.guild.members:
            #prob = fuzz.ratio(username, ingameName)
            uqprob = max(fuzz.UQRatio(username, discordUser.nick or '-'),fuzz.UQRatio(username, discordUser.name or '-'))
            #uwprob = fuzz.UWRatio(username, ingameName)
            if uqprob > maxProb:
                maxProb = uqprob
                maxUser = discordUser
  
        if not maxUser:
            await message.channel.send(f'User {username} not found in discord Server')
            return
        discordUser = maxUser
        
        async with message.channel.typing():
            userid = memberMap[steamName]
            roleList = getPlayerRoles(userid)
            #print(f'{maxName} has ID {userid} and roles {str(roleList)}')
            newRole = False
            for role in roleList:
                roleObj = discord.utils.get(message.guild.roles, name=role)
                if roleObj is None:
                    await message.channel.send(f'Role {role} was not found')
                    continue
                if roleObj in discordUser.roles:
                    print(f'{maxName} already has role {role}')
                    continue
                await discordUser.add_roles(roleObj)
                await message.channel.send(f'Assigned role {role} to {discordUser.mention}')
                newRole = True
            if not newRole:
                await message.channel.send(f'No new roles for you')