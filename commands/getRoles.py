from commands.base_command  import BaseCommand

from functions              import getUserIDbySnowflakeAndClanLookup, getFullMemberMap, getNameToHashMapByClanid
from functions              import getPlayerRoles, assignRolesToUser,removeRolesFromUser, getUserMap,fullMemberMap, isUserInClan
from dict                   import requirementHashes, clanids

import discord

raiderText = '⁣           Raider       ⁣'
achText = '⁣        Achievements       ⁣'

fullMemberMap = getFullMemberMap()

class getRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
<<<<<<< HEAD
        description = "Assigns you all the roles you've earned"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):

        destinyID = getUserMap(message.author.id)
        if not destinyID:
<<<<<<< HEAD
            destinyID = getUserIDbySnowflakeAndClanLookup(message.author,fullMemberMap)
=======
            await message.channel.send('please sign up using !registerbo')
            return
>>>>>>> 08badc0b0ea658b616d946315067dc05956aee2e
        
        async with message.channel.typing():
            (roleList,removeRoles) = getPlayerRoles(destinyID)
            await assignRolesToUser(roleList, message.author, message.guild)
            await removeRolesFromUser(removeRoles,message.author,message.guild)

            for role in roleList:
                if role in requirementHashes['Addition']:
                    await message.author.add_roles(discord.utils.get(message.guild.roles, name=achText))
                else:
                    await message.author.add_roles(discord.utils.get(message.guild.roles, name=raiderText))
<<<<<<< HEAD
            rolesgiven = ', '.join(roleList)
            await message.channel.send(f'Added the roles {rolesgiven} to user {message.author.mention}')

#improvable TODO
class removeAllRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] removes a certain users roles"
        params = ['User']
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer') 
        discordID = params[0]
        if admin not in message.author.roles and dev not in message.author.roles and not message.author.id == params[0]:
            await message.channel.send('You are not allowed to do that')
            return
        await removeRolesFromUser(removeRoles, client.get_user(discordID), message.guild)

class checkNames(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] check name mappings"
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

class listDescend(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] list all discordusers that are in the 'The Descent' clan"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        descendid = 4107840
        nameidmap = getNameToHashMapByClanid(descendid)
        nameidarr = [(name,id_) for (name,id_) in nameidmap.items()]
        namearr = [name for (name, _) in nameidarr]
        idarr = [int(id_) for (_, id_) in nameidarr]
        negativelist = [id_ for id_ in idarr]
        #await message.channel.send(f'All of Descend:{zip(namearr,idarr)}')
        async with message.channel.typing():
            await message.channel.send(f'**Members of Descend in this discord:**')
            for discordUser in message.guild.members:
                destinyID = getUserMap(discordUser.id)
                if not destinyID:
                    destinyID = getUserIDbySnowflakeAndClanLookup(discordUser,nameidmap)
                if not destinyID:
                    continue
                if destinyID in idarr:
                    negativelist.remove(destinyID)
                    name = None
                    for (user, userid) in zip(namearr,idarr):
                        if userid == destinyID:
                            name = user
                    await message.channel.send(f'{discordUser.name} ({discordUser.nick}) as {name}')
            await message.channel.send(f'**Members of Descend __not__ in this discord:**')
            for dID in negativelist:
                for (user, userid) in zip(namearr,idarr):
                    if dID == userid:
                        await message.channel.send(f'{user} : {userid}')
=======
            await message.channel.send(f'you have the roles {", ".join(roleList)}')
>>>>>>> 08badc0b0ea658b616d946315067dc05956aee2e


class assignAllRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] Assigns everyone the roles they earned"
        params = []
        super().__init__(description, params)
    
    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer') 
        destinyID = params[0]
        if admin not in message.author.roles and dev not in message.author.roles and not message.author.id == params[0]:
            await message.channel.send('You are not allowed to do that')
            return

        for discordUser in message.guild.members:
            destinyID = getUserMap(discordUser.id)
            if not destinyID:
                destinyID = getUserIDbySnowflakeAndClanLookup(discordUser,fullMemberMap)

            async with message.channel.typing():
                (newRoles, removeRoles) = getPlayerRoles(destinyID)
                await assignRolesToUser(newRoles, discordUser, message.guild)
                await removeRolesFromUser(removeRoles, discordUser, message.guild)
            await message.channel.send('All roles assigned')
