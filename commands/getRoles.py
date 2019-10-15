from commands.base_command  import BaseCommand
from utils                  import get_emoji
from random                 import randint

from functions              import getNameToHashMapByClanid
from fuzzywuzzy             import fuzz
from fuzzywuzzy             import process
#from discord                import *

from functions import getPlayerRoles
from dict import requirementHashes
import discord

base_uri = 'https://discordapp.com/api/v7'
bungie_base = ''
bungie_getMembershipId_by_bungieName = '/Destiny/[MembershipType]/Stats/GetMembershipIdByDisplayName/[DisplayName]'
memberMap = getNameToHashMapByClanid(2784110)

raiderText = '⁣           Raider       ⁣'
achText = '⁣        Achievements       ⁣'


async def assignRolesToUser(roleList, discordUser, message):
    newRole = False
    for role in roleList:
        roleObj = discord.utils.get(message.guild.roles, name=role)
        if roleObj is None:
            await message.channel.send(f'Role {role} was not found')
            continue
        if roleObj not in discordUser.roles:
            if role in requirementHashes['Addition']:
                await discordUser.add_roles(discord.utils.get(message.guild.roles, name=achText))
            else:
                await discordUser.add_roles(discord.utils.get(message.guild.roles, name=raiderText))
            await discordUser.add_roles(roleObj)
            await message.channel.send(f'Assigned role {role} to {discordUser.nick or discordUser.name}')
            newRole = True
    if not newRole:
        await message.channel.send(f'No new roles')

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
            uqprob = fuzz.UQRatio(username, ingameName)
            if uqprob > maxProb:
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
            uqprob = max(fuzz.UQRatio(username, discordUser.nick or '-'),fuzz.UQRatio(username, discordUser.name or '-'))
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
            await assignRolesToUser(roleList, discordUser, message)

class getAllRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "gets the roles of a bloodoakplayer by ingameName"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        for discordUser in message.guild.members:
            username = discordUser.nick or discordUser.name
            maxName = None
            maxProb = 50
            for ingameName in memberMap.keys():
                uqprob = fuzz.UQRatio(username, ingameName)
                if uqprob > maxProb:
                    maxProb = uqprob
                    maxName = ingameName
            if not maxName:
                await message.channel.send(f'User {username} not found in BO I')
                continue
            steamName = maxName
            async with message.channel.typing():
                userid = memberMap[steamName]
                roleList = getPlayerRoles(userid)
                await assignRolesToUser(roleList, discordUser, message)