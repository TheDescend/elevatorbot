import discord
from discord.ext import commands

from commands.base_command import BaseCommand
from events.backgroundTasks import updateActivityDB
from functions.dataLoading import updateDB, getNameToHashMapByClanid
from functions.database import lookupDestinyID, lookupDiscordID, getLastRaid, getFlawlessList
from functions.formating import embed_message
from functions.roles import assignRolesToUser, removeRolesFromUser, getPlayerRoles, hasRole
from functions.miscFunctions import hasAdminOrDevPermissions, hasMentionPermission
from static.dict import requirementHashes, clanids
from static.globals import dev_role_id

import time


class getRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Assigns you all the roles you've earned"
        topic = "Roles"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        # check perm for mention, otherwise abort
        if not (await hasMentionPermission(message, mentioned_user)):
            return

        destinyID = lookupDestinyID(mentioned_user.id)

        if not destinyID:
            await message.channel.send(embed=embed_message(
                'Error',
                'Didn\'t find your destiny profile, sorry'
            ))
            return

        wait_msg = await message.channel.send(embed=embed_message(
            f'Hi, {mentioned_user.display_name}',
            "Your data will be available soon™"
        ))

        await updateDB(destinyID)

        print('done updating db')
        
        async with message.channel.typing():
            roles_at_start = [role.name for role in mentioned_user.roles]

            (roleList, removeRoles) = await getPlayerRoles(destinyID, roles_at_start)

            roles_assignable = await assignRolesToUser(roleList, mentioned_user, message.guild)
            await removeRolesFromUser(removeRoles, mentioned_user, message.guild)

            if not roles_assignable:
                await wait_msg.delete()
                await message.channel.send(embed=embed_message(
                    'Error',
                    f'You seem to have been banned from acquiring any roles.\nIf you believe this is a mistake, refer to the admin team or DM <@386490723223994371>'
                ))
                return

            #roles_now = [role.name for role in mentioned_user.roles]

            old_roles = {}
            updated_roles_member = await mentioned_user.guild.fetch_member(mentioned_user.id)
            roles_now = [role.name for role in updated_roles_member.roles]
            new_roles = {}
            for topic, topicroles in requirementHashes.items():
                topic = topic.replace("Y1", "Year One")
                topic = topic.replace("Y2", "Year Two")
                topic = topic.replace("Y3", "Year Three")
                topic = topic.replace("Y4", "Year Four")

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
                await wait_msg.delete()
                await message.channel.send(embed=embed_message(
                    'Error',
                    f'You don\'t seem to have any roles.\nIf you believe this is an Error, refer to one of the <@&{dev_role_id}>\nOtherwise check <#686568386590802000> to see what you could acquire'
                ))
                return

            embed = embed_message(
                f"{mentioned_user.display_name}'s new Roles",
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

            await wait_msg.delete()
            await message.channel.send(
                embed=embed,
                reference=message,
                mention_author=True
            )

class lastRaid(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Gets your last raid"
        topic = "Roles"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received

    async def handle(self, params, message, mentioned_user, client):
        destinyID = lookupDestinyID(mentioned_user.id)
        await updateDB(destinyID)
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

    async def handle(self, params, message, mentioned_user, client):
        async with message.channel.typing():
            destinyID = lookupDestinyID(mentioned_user.id)
            await updateDB(destinyID)
            await message.channel.send(getFlawlessList(destinyID))


#improvable TODO
class removeAllRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] removes a certain users roles"
        params = []
        topic = "Roles"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message) and not message.author.id == mentioned_user.id:
            return

        roles = []
        for yeardata in requirementHashes.values():		
            for role in yeardata.keys():
                roles.append(role)
        await removeRolesFromUser(roles, mentioned_user, message.guild)


class checkNames(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] check name mappings"
        topic = "Roles"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        messagetext = ""
        for discordUser in message.guild.members:
            if destinyID := lookupDestinyID(discordUser.id):
                messagetext += f'{discordUser.name} ({discordUser.nick}): https://raid.report/pc/{destinyID}\n' #TODO make console-flexible
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
    async def handle(self, params, message, mentioned_user, client):
        naughtylist = []
        for clanid,name in clanids.items():
            await message.channel.send(f'checking clan {name}')
            clanmap = await getNameToHashMapByClanid(clanid)
            for username, userid in clanmap.items():
                discordID = lookupDiscordID(userid)
                if discordID: #if the matching exists in the DB, check whether the discordID is valid and in the server
                    guy = client.get_user(discordID)
                    if not guy: #TODO implement actual 'present in server'-check
                        await message.channel.send(f'[ERROR] {username} with destinyID {userid} has discordID {discordID} registered, but it is faulty or user left the server')
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
    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        await message.channel.send('Updating DB...')

        update = updateActivityDB()
        await update.run(client)

        await message.channel.send('Assigning roles...')
        donemessage = ""
        for discordUser in message.guild.members:
            destinyID = lookupDestinyID(discordUser.id)
            if not destinyID:
                #await message.channel.send(f'No destinyID found for {discordUser.name}')
                continue

            async with message.channel.typing():

                (newRoles, removeRoles) = await getPlayerRoles(destinyID, [role.name for role in discordUser.roles])
                await assignRolesToUser(newRoles, discordUser, message.guild)
                await removeRolesFromUser(removeRoles, discordUser, message.guild)

                roletext = ', '.join(newRoles)
                donemessage += f'Assigned roles {roletext} to {discordUser.name}\n'
        
        await message.channel.send(donemessage)

        #await message.channel.send('All roles assigned')


class roleRequirements(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Shows you what you need for a role"
        topic = "Roles"
        params = ["role"]
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
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

        #Get user details and run analysis
        async with message.channel.typing():
            destinyID = lookupDestinyID(mentioned_user.id)
            wait_msg = await message.channel.send(embed=embed_message(
                f'Hi, {mentioned_user.name}',
                "Your data will be available shortly"
            ))

            await updateDB(destinyID)
            reqs = await hasRole(destinyID, f_role, f_year, br=False)


            print(reqs[1])

            embed = embed_message(
                f"{mentioned_user.display_name}'s '{f_role}' Eligibility"
            )

            for req in reqs[1]:
                embed.add_field(name=req, value=reqs[1][req], inline=True)
            
            await wait_msg.delete()
            await message.channel.send(
                embed=embed,
                reference=message,
                mention_author=True
            )
