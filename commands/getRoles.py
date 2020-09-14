from commands.base_command  import BaseCommand

from static.dict                    import requirementHashes, clanids
from functions.database             import lookupDestinyID, lookupDiscordID, getLastRaid, getFlawlessList
from functions.dataLoading          import updateDB, initDB, getNameToHashMapByClanid
from functions.dataTransformation   import getFullMemberMap
from functions.roles                import hasAdminOrDevPermissions, assignRolesToUser, removeRolesFromUser, getPlayerRoles, hasRole
from functions.formating import     embed_message


import discord
import json

from discord.ext import commands

raiderText = '⁣           Raider       ⁣'
raiderId = 670385313994113025
achText = '⁣        Achievements       ⁣'
achId = 670385837044662285


class getRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Assigns you all the roles you've earned"
        topic = "Roles"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        # check if message too long
        if len(params) > 1:
            await message.channel.send(embed=embed_message(
                'Error',
                'Incorrect formatting, correct usage is: \n\u200B\n `!getroles *<user>`'
            ))
            return

        user = message.author
        if len(params) == 1:
            # check if user has permission to use this command
            if not await hasAdminOrDevPermissions(message) and not message.author.id == params[0]:
                return

            ctx = await client.get_context(message)
            try:
                user = await discord.ext.commands.MemberConverter().convert(ctx, params[0])
            except:
                await message.channel.send(
                    embed=embed_message(
                        'Error',
                        'User not found, make sure the spelling/id is correct'
                    ))
                return
        destinyID = lookupDestinyID(user.id)

        if not destinyID:
            await message.channel.send(embed=embed_message(
                'Error',
                'Didn\'t find your destiny profile, sorry'
            ))
            return

        updateDB(destinyID)
        
        async with message.channel.typing():
            roles_at_start = [role.name for role in user.roles]
            (roleList,removeRoles) = getPlayerRoles(destinyID, roles_at_start)

            await assignRolesToUser(roleList, user, message.guild)
            await removeRolesFromUser(removeRoles, user, message.guild)

            for role in roleList:
                if role in requirementHashes['Addition']:
                    await user.add_roles(discord.utils.get(message.guild.roles, id=achId ))#,name=achText))
                else:
                    await user.add_roles(discord.utils.get(message.guild.roles, id=raiderId ))#,name=raiderText))

            roles_now = [role.name for role in user.roles]

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
                f"{user.display_name}'s new Roles",
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
        topic = "Roles"
        params = []
        super().__init__(description, params, topic)

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
        description = "[dev] flaweless hashes"
        topic = "Roles"
        params = []
        super().__init__(description, params, topic)

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

#improvable TODO
class removeAllRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] removes a certain users roles"
        params = ['User']
        topic = "Roles"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message) and not message.author.id == params[0]:
            return

        discordID = params[0]
        roles = []
        for yeardata in requirementHashes.values():		
            for role in yeardata.keys():
                roles.append(role)
        await removeRolesFromUser(roles, client.get_user(int(discordID)), message.guild)

class checkNames(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] check name mappings"
        topic = "Roles"
        params = []
        super().__init__(description, params, topic)

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
        topic = "Roles"
        params = []
        super().__init__(description, params, topic)

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
        topic = "Roles"
        params = []
        super().__init__(description, params, topic)
    
    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
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


class roleRequirements(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Shows you what you need for a role"
        topic = "Roles"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        # check if message too short
        if len(params) == 0:
            await message.channel.send(embed=embed_message(
                'Error',
                'Incorrect formatting, correct usage is: \n\u200B\n `!roleRequirements <role>`'
            ))
            return

        given_role = " ".join(params)

        f_year = ""
        f_role = ""
        found = False
        for topic, roles in requirementHashes.items():
            if found:
                break
            else:
                for role, roledata in roles.items():
                    if given_role.lower() == role.lower():
                        found = True
                        f_year = topic
                        f_role = role
                        break

        if not found:
            await message.channel.send(embed=embed_message(
                'Error',
                f"I don't know that role, please make sure it's spelled correctly!"
            ))
            return

        async with message.channel.typing():
            destinyID = lookupDestinyID(message.author.id)
            reqs = hasRole(destinyID, f_role, f_year, br=False)


            print(reqs[1])

            embed = embed_message(
                f"{message.author.display_name}'s '{f_role}' Eligibility"
            )

            for req in reqs[1]:
                embed.add_field(name=req, value=reqs[1][req], inline=True)

            await message.channel.send(embed=embed)
