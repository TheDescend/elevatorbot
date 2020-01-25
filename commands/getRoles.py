from commands.base_command  import BaseCommand

from functions              import getUserIDbySnowflakeAndClanLookup, getFullMemberMap
from functions              import getPlayerRoles, assignRolesToUser,removeRolesFromUser, getUserMap
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

        destinyID = getUserMap(message.author.id)
        if destinyID:
            await message.channel.send('https://raid.report/pc/' + destinyID)
            return

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


class checkNames(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "check name mappings"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        for discordUser in message.guild.members:
            destinyID = None
            destinyID = getUserMap(discordUser.id)
            if destinyID:
                await message.channel.send(f'{discordUser.name} ({discordUser.nick}): https://raid.report/pc/{destinyID}')
                continue
            destinyID = getUserIDbySnowflakeAndClanLookup(discordUser,fullMemberMap)
            await message.channel.send(f'{discordUser.name} ({discordUser.nick}): https://raid.report/pc/{destinyID}')


class assignAllRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Assigns everyone the roles they earned"
        params = []
        super().__init__(description, params)
    
    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        for discordUser in message.guild.members:
            
            destinyID = getUserMap(discordUser.id)
            if not destinyID:
                destinyID = getUserIDbySnowflakeAndClanLookup(discordUser,fullMemberMap)

            async with message.channel.typing():
                (newRoles, removeRoles) = getPlayerRoles(destinyID)
                await assignRolesToUser(newRoles, discordUser, message.guild)
                await removeRolesFromUser(removeRoles, discordUser, message.guild)
            await message.channel.send('All roles assigned')
