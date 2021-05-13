from commands.base_command import BaseCommand
from events.backgroundTasks import updateActivityDB
from functions.dataLoading import updateDB
from functions.database import lookupDestinyID, getLastActivity, getFlawlessList
from functions.formating import embed_message
from functions.miscFunctions import hasMentionPermission, hasAdminOrDevPermissions
from functions.roleLookup import getPlayerRoles, assignRolesToUser, removeRolesFromUser, hasRole
from static.dict import requirementHashes
from static.globals import dev_role_id


# has been slashified
class roles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Shows you what roles you can still achieve in this clan"
        params = []
        topic = "Destiny"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        async with message.channel.typing():
            embed = embed_message(
                f"{mentioned_user.display_name}'s missing Roles"
            )

            active_roles, deprecated_roles = self.missingRoles(mentioned_user)

            # do the missing roles display
            embed.add_field(name="⁣", value=f"__**Achievable Roles:**__", inline=False)

            # only do this if there are roles to get
            if active_roles:
                for topic in active_roles:
                    embed.add_field(name=topic, value=("\n".join(active_roles[topic]) or "None"), inline=True)
            else:
                embed.add_field(name="Wow, you got every single role that is currently achievable. Congrats!", value="⁣", inline=False)

            # Do the same for the deprecated roles
            if deprecated_roles:
                embed.add_field(name="⁣", value=f"__**Deprecated Roles:**__", inline=False)
                for topic in deprecated_roles:
                    embed.add_field(name=topic, value=("\n".join(deprecated_roles[topic]) or "None"), inline=True)

            await message.reply(embed=embed)

    def missingRoles(self, user):
        roles = {}
        deprecated_roles = {}

        # get list of roles available
        for category, x in requirementHashes.items():
            for role, req in x.items():
                # depending on if its deprecated or not, add to respective dict
                if "deprecated" not in req:
                    try:
                        roles[category].append(role)
                    except KeyError:
                        roles[category] = [role]
                else:
                    try:
                        deprecated_roles[category].append(role)
                    except KeyError:
                        deprecated_roles[category] = [role]

        # remove the roles from dict(roles) that are already earned
        user_roles = [role.name for role in user.roles]
        for role in user_roles:
            for category in roles:
                try:
                    roles[category].remove(role)
                    break
                except ValueError:
                    pass
            for category in deprecated_roles:
                try:
                    deprecated_roles[category].remove(role)
                    break
                except ValueError:
                    pass

        # remove those roles, where a superior role exists
        for category, x in requirementHashes.items():
            for role, roledata in x.items():
                if 'replaced_by' in roledata.keys():
                    for superior in roledata['replaced_by']:
                        if superior in user_roles:
                            for category in roles:
                                try:
                                    roles[category].remove(role)
                                    break
                                except ValueError:
                                    pass
                            for category in deprecated_roles:
                                try:
                                    deprecated_roles[category].remove(role)
                                    break
                                except ValueError:
                                    pass

        # remove the empty categories
        for role, roledata in roles.copy().items():
            if not roledata:
                roles.pop(role)
        for role, roledata in deprecated_roles.copy().items():
            if not roledata:
                deprecated_roles.pop(role)

        return roles, deprecated_roles

# has been slashified
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

            roles_assignable = await assignRolesToUser(roleList, mentioned_user, message.guild, reason="Role Update")
            await removeRolesFromUser(removeRoles, mentioned_user, message.guild, reason="Role Update")

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

# has been slashified
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
        await message.channel.send(getLastActivity(destinyID, mode=4))


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
            await message.channel.send(await getFlawlessList(destinyID))


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
        await removeRolesFromUser(roles, mentioned_user, message.guild, reason="Role Update")


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
                await assignRolesToUser(newRoles, discordUser, message.guild, reason="Role Update")
                await removeRolesFromUser(removeRoles, discordUser, message.guild, reason="Role Update")

                roletext = ', '.join(newRoles)
                donemessage += f'Assigned roles {roletext} to {discordUser.name}\n'

        await message.channel.send(donemessage)

        #await message.channel.send('All roles assigned')

# has been slashified
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
                f'Hi, {mentioned_user.display_name}',
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