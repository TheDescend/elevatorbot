from commands.base_command  import BaseCommand

from functions              import getUserIDbySnowflakeAndClanLookup, getFullMemberMap
from functions              import getPlayerRoles, assignRolesToUser,removeRolesFromUser, getUserMap
from dict                   import requirementHashes, clanids

import discord

raiderText = '⁣           Raider       ⁣'
achText = '⁣        Achievements       ⁣'

fullMemberMap = getFullMemberMap()

class getID(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] gets destinyID from charley"
        params = ['discordID'] 
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):

        discordID = params[0]
        charley = client.get_user(296023718839451649)
        await charley.send('!time 171650677607497730')
        timemessage = await client.wait_for('message')
        print(timemessage)
        # if destinyID:
        #     await message.channel.send('https://raid.report/pc/' + destinyID)
        #     return

        # destinyID = getUserIDbySnowflakeAndClanLookup(message.author,fullMemberMap)
        
        # async with message.channel.typing():
        #     (roleList,removeRoles) = getPlayerRoles(destinyID)
        #     await assignRolesToUser(roleList, message.author, message.guild)
        #     await removeRolesFromUser(removeRoles,message.author,message.guild)

        #     for role in roleList:
        #         if role in requirementHashes['Addition']:
        #             await message.author.add_roles(discord.utils.get(message.guild.roles, name=achText))
        #         else:
        #             await message.author.add_roles(discord.utils.get(message.guild.roles, name=raiderText))