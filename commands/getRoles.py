from commands.base_command  import BaseCommand

from functions              import getUserIDbySnowflakeAndClanLookup, getFullMemberMap
from functions              import getPlayerRoles, assignRolesToUser,removeRolesFromUser
from dict                   import requirementHashes, clanids

import discord

raiderText = '⁣           Raider       ⁣'
achText = '⁣        Achievements       ⁣'

fullMemberMap = getFullMemberMap()

class getRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "gets the roles of a you"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        username = message.author.display_name
        if len(params) == 1:
            username = str(params[0])
        
        destinyID = getUserIDbySnowflakeAndClanLookup(message.author,fullMemberMap)
        
        async with message.channel.typing():
            (roleList,removeRoles) = getPlayerRoles(destinyID)
            await assignRolesToUser(roleList, message.author, message.guild)
            await removeRolesFromUser(removeRoles,message.author,message.guild)

            for role in roleList:
                if role in requirementHashes['Addition']:
                    await message.author.add_roles(discord.utils.get(message.guild.roles, name=achText))
                else:
                    await message.author.add_roles(discord.utils.get(message.guild.roles, name=raiderText))


class getAllRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Assigns everyone the roles they earned"
        params = []
        super().__init__(description, params)
    
    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        BOrole = discord.utils.get(message.guild.roles, name='Bloodoak')
        for discordUser in message.guild.members:
            if not BOrole in discordUser.roles:
                continue
            destinyID = getUserIDbySnowflakeAndClanLookup(discordUser,fullMemberMap)
            async with message.channel.typing():
                (newRoles, removeRoles) = getPlayerRoles(destinyID)
                await assignRolesToUser(newRoles, discordUser, message.guild)
                await removeRolesFromUser(removeRoles, discordUser, message.guild)
            await message.channel.send('All roles assigned')
