from commands.base_command import BaseCommand
from functions.database import getToken, lookupDiscordID
from functions.formating import embed_message
from functions.network import getJSONfromURL
from functions.roleLookup import assignRolesToUser, removeRolesFromUser
from functions.miscFunctions import hasAdminOrDevPermissions
from static.config import CLANID
from static.globals import registered_role_id, not_registered_role_id, member_role_id

import discord


# todo: slashify when you can hide commands
class addRolesToRegistered(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Assigns @Registered or @Not Registered to everyone"
        topic = "Registration"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        if not await hasAdminOrDevPermissions(message):
            return
        await message.channel.send("Working...")
        notregisteredlist = []
        registeredlist = []
        for member in message.guild.members:
            if not member.pending:
                await removeRolesFromUser([registered_role_id], member, message.guild)
                await removeRolesFromUser([not_registered_role_id], member, message.guild)

                if getToken(member.id):
                    await assignRolesToUser([registered_role_id], member, message.guild)
                    registeredlist.append(member.name)
                else:
                    await assignRolesToUser([not_registered_role_id], member, message.guild)
                    notregisteredlist.append(member.name)

                roleids = [role.id for role in member.roles]
                if (registered_role_id not in roleids) and (not_registered_role_id not in roleids):
                    print(getToken(member.id))
                    print(member.id)
                    break
        

        await message.channel.send(f"Registered:\n {','.join(registeredlist)}")
        await message.channel.send(f"**NOT** registered:\n {','.join(notregisteredlist)}")


# todo: slashify when you can hide commands
class whoIsNotRegistered(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Blames ppl who are not registered"
        topic = "Registration"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        people = []
        for member in message.guild.members:
            if not getToken(member.id):
                people.append(member.name)

        await message.channel.send(", ".join(people))


# todo: slashify when you can hide commands
class findNaughtyClanMembers(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Blames ppl who are in the d2 clan, but do not fulfill requirements"
        topic = "Registration"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        # get all clan members discordID
        memberlist = []
        for member in (await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"))["Response"]["results"]:
            destinyID = int(member["destinyUserInfo"]["membershipId"])
            memberlist.append(destinyID)

        not_in_discord_or_registered = []       # list of destinyID
        no_token = []                           # list of guild.member.mention
        not_accepted_rules = []                 # list of guild.member.mention

        # loop through all members and check requirements
        for destinyID in memberlist:
            # check if in discord or still having the old force registration
            discordID = lookupDiscordID(destinyID)
            if discordID is None:
                not_in_discord_or_registered.append(str(destinyID))
                continue
            member = message.guild.get_member(discordID)
            if member is None:
                not_in_discord_or_registered.append(str(destinyID))
                continue

            # check if no token
            if not getToken(discordID):
                no_token.append(member.mention)

            # check if accepted rules
            if member.pending:
                not_accepted_rules.append(member.mention)

        if not_in_discord_or_registered:
            textstr = ", ".join(not_in_discord_or_registered)
            while tempstr := textstr[:1900]:
                await message.channel.send(
                    "**These destinyIDs are not in discord, or have not registered with the bot**\n"
                    + tempstr
                )
                textstr = textstr[1900:]

        if no_token:
            textstr = ", ".join(no_token)
            while tempstr := textstr[:1900]:
                await message.channel.send(
                    "**These users have no token and need to register with the bot** \n"
                    + tempstr
                )
                textstr = textstr[1900:]

        if not_accepted_rules:
            textstr = ", ".join(not_accepted_rules)
            while tempstr := textstr[:1900]:
                await message.channel.send(
                    "**These users have not yet accepted the rules**\n"
                    + tempstr
                )
                textstr = textstr[1900:]

