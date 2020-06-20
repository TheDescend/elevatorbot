from commands.base_command  import BaseCommand

from static.dict                    import requirementHashes, clanids
from functions.database             import lookupDestinyID, lookupDiscordID, getLastRaid, getFlawlessList
from functions.dataLoading          import updateDB, initDB, getNameToHashMapByClanid
from functions.dataTransformation   import getFullMemberMap
from functions.roles                import assignRolesToUser, removeRolesFromUser, getPlayerRoles
from functions.formating import     embed_message


import discord
import json

from discord.ext import commands

raiderText = '⁣           Raider       ⁣'
achText = '⁣        Achievements       ⁣'

class getRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Assigns you all the roles you've earned"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        if params:
            await message.channel.send(embed=embed_message(
                'Error',
                f'You can\'t do this for other users\n Use !setroles {params[0]} instead'
            ))
            return
        destinyID = lookupDestinyID(message.author.id)

        if not destinyID:
            await message.channel.send(embed=embed_message(
                'Error',
                'Didn\'t find your destiny profile, sorry'
            ))
            return

        updateDB(destinyID)
        
        async with message.channel.typing():
            roles_at_start = [role.name for role in message.author.roles]
            (roleList,removeRoles) = getPlayerRoles(destinyID, roles_at_start)

            await assignRolesToUser(roleList, message.author, message.guild)
            await removeRolesFromUser(removeRoles,message.author,message.guild)

            for role in roleList:
                if role in requirementHashes['Addition']:
                    await message.author.add_roles(discord.utils.get(message.guild.roles, name=achText))
                else:
                    await message.author.add_roles(discord.utils.get(message.guild.roles, name=raiderText))

            roles_now = [role.name for role in message.author.roles]

            old_roles = {}
            new_roles = {}
            for topic, topicroles in requirementHashes.items():
                topic = topic.replace("Y1", "Year One")
                topic = topic.replace("Y2", "Year Two")
                topic = topic.replace("Y3", "Year Three")
                topic = topic.replace("Addition", "Miscellaneous")

                for role in topicroles.keys():
                    if role in roles_at_start:
                        try:
                            old_roles[topic].append(role)
                        except KeyError:
                            old_roles[topic] = [role]
                    elif (role not in roles_at_start) and (role in roles_now):
                        try:
                            new_roles[topic].append(role)
                        except KeyError:
                            new_roles[topic] = [role]

            if not roleList:
                await message.channel.send(embed=embed_message(
                    'Error',
                    f'You don\'t seem to have any roles.\nIf you believe this is an Error, refer to one of the <@&670397357120159776>\nOtherwise check <#686568386590802000> to see what you could acquire'
                ))
                return

            embed = embed_message(
                f"{message.author.name}'s new Roles",
                f'__Previous Roles:__'
            )
            if not old_roles:
                embed.add_field(name=f"You didn't have any roles before", value="⁣", inline=True)

            for topic in old_roles:
                roles = []
                for role in topic:
                    roles.append(role)
                embed.add_field(name=topic, value="\n".join(old_roles[topic]), inline=True)

            embed.add_field(name="⁣", value=f"__New Roles:__", inline=False)
            if not new_roles:
                embed.add_field(name="No new roles have been achieved", value="⁣", inline=True)

            for topic in new_roles:
                roles = []
                for role in topic:
                    roles.append(role)
                embed.add_field(name=topic, value="\n".join(new_roles[topic]), inline=True)

            await message.channel.send(embed=embed)

class lastRaid(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "gets your last raid"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received

    async def handle(self, params, message, client):
        ctx = await client.get_context(message)
        user = message.author
        if params:
            user = await commands.MemberConverter().convert(ctx, params[0])

        destinyID = lookupDestinyID(user.id)
        updateDB(destinyID)
        await message.channel.send(getLastRaid(destinyID))

class flawlesses(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "flaweless hashes"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received

    async def handle(self, params, message, client):
        ctx = await client.get_context(message)
        user = message.author
        if params:
            user = await commands.MemberConverter().convert(ctx, params[0])
        async with message.channel.typing():
            destinyID = lookupDestinyID(user.id)
            updateDB(destinyID)
            await message.channel.send(getFlawlessList(destinyID))

class setRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[admin] Assigns the mentioned user his/her earned roles"
        params = ['user']
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received

    async def handle(self, params, message, client):
        ctx = await client.get_context(message)
        user = await commands.MemberConverter().convert(ctx, params[0])
        destinyID = lookupDestinyID(user.id)
        if not destinyID:
            await message.channel.send(embed=embed_message(
                'Error',
                'Didn\'t find the destiny profile, sorry'
            ))
            return
        status_msg = await message.channel.send(embed=embed_message(
            'Working...',
            'Updating DB and assigning roles...'
        ))
        status_msg = await message.channel.fetch_message(status_msg.id)
        updateDB(destinyID)
        
        async with message.channel.typing():
            (roleList,removeRoles) = getPlayerRoles(destinyID, [role.name for role in user.roles])
            
            await assignRolesToUser(roleList, user, message.guild)
            await removeRolesFromUser(removeRoles,user,message.guild)

            for role in roleList:
                if role in requirementHashes['Addition']:
                    await user.add_roles(discord.utils.get(message.guild.roles, name=achText))
                else:
                    await user.add_roles(discord.utils.get(message.guild.roles, name=raiderText))
            rolesgiven = ', '.join(roleList)
            if len(rolesgiven) == 0:
                await status_msg.edit(embed=embed_message(
                    'Error',
                    f'You don\'t seem to have any roles.\nIf you believe this is an Error, refer to one of the @Developers\nOtherwise check <#686568386590802000> to see what you could acquire'
                ))
                return
            await status_msg.edit(embed=embed_message(
                f'{user.name} Roles',
                f'Added the roles {rolesgiven}'
            ))

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
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to do that'
            ))
            return
        roles = []
        for yeardata in requirementHashes.values():		
            for role in yeardata.keys():
                roles.append(role)
        await removeRolesFromUser(roles, client.get_user(int(discordID)), message.guild)

class checkNames(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] check name mappings"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        messagetext = ""
        for discordUser in message.guild.members:
            if destinyID := lookupDestinyID(discordUser.id):
                messagetext += f'{discordUser.name} ({discordUser.nick}): https://raid.report/pc/{destinyID}\n'
            else:
                messagetext += f'{discordUser.name} ({discordUser.nick}): Not found\n'
        await message.channel.send(messagetext)

class checkNewbies(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] check people"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        naughtylist = []
        for clanid,name in clanids.items():
            await message.channel.send(f'checking clan {name}')
            clanmap = getNameToHashMapByClanid(clanid)
            for username, userid in clanmap.items():
                discordID = lookupDiscordID(userid)
                if discordID:
                    user = client.get_user(discordID)
                    if not user:
                        await message.channel.send(f'[ERROR] {username} with destinyID {userid} has discordID {discordID} but it is faulty')
                        continue
                    #await message.channel.send(f'{username} is in Discord with name {user.name}')
                else:
                    naughtylist.append(username)
                    await message.channel.send(f'{username} with ID {userid} is not in Discord (or not recognized by the bot)')
        await message.channel.send(f'users to check: {", ".join(naughtylist)}')


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
        if admin not in message.author.roles and dev not in message.author.roles:
            await message.channel.send('You are not allowed to do that')
            return
        await message.channel.send('Updating DB...')
        initDB()
        await message.channel.send('Assigning roles...')
        for discordUser in message.guild.members:
            destinyID = lookupDestinyID(discordUser.id)
            if not destinyID:
                await message.channel.send(f'No destinyID found for {discordUser.name}')
                continue

            async with message.channel.typing():
                (newRoles, removeRoles) = getPlayerRoles(destinyID, [role.name for role in discordUser.roles])
                await assignRolesToUser(newRoles, discordUser, message.guild)
                await removeRolesFromUser(removeRoles, discordUser, message.guild)

                roletext = ', '.join(newRoles)
                await message.channel.send(f'Assigned roles {roletext} to {discordUser.name}')

        await message.channel.send('All roles assigned')
