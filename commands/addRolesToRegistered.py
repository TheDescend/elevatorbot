from commands.base_command import BaseCommand
from functions.database import getToken, lookupDiscordID
from functions.network import getJSONfromURL
from functions.roles import assignRolesToUser, removeRolesFromUser
from functions.roles import hasAdminOrDevPermissions
from static.config import CLANID
from static.globals import registered_role_id, not_registered_role_id


class addRolesToRegistered(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Assigns @Registered or @Not Registered to everyone"
        topic = "Registration"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        if not await hasAdminOrDevPermissions(message):
            return
        await message.channel.send("Working...")
        for member in message.guild.members:
            await removeRolesFromUser([registered_role_id], member, message.guild)
            await removeRolesFromUser([not_registered_role_id], member, message.guild)

            if getToken(member.id):
                await assignRolesToUser([registered_role_id], member, message.guild)
                await message.channel.send(f"add @Registered to {member.name}")
            else:
                await assignRolesToUser([not_registered_role_id], member, message.guild)
                await message.channel.send(f"add @Not Registered to {member.name}")

        await message.channel.send("Done")


class whoIsNotRegistered(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Blames ppl who are not registered"
        topic = "Registration"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        people = []
        for member in message.guild.members:
            if not getToken(member.id):
                people.append(member.name)

        await message.channel.send(", ".join(people))


class whoIsNotRegisteredAndInClan(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Blames ppl who are not registered and are in the d2 clan"
        topic = "Registration"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        # get all clan members discordID
        memberlist = []
        for member in (await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"))["Response"]["results"]:
            destinyID = int(member["destinyUserInfo"]["membershipId"])
            discordID = lookupDiscordID(destinyID)
            if discordID is not None:
                memberlist.append(discordID)

        people = []
        for member in message.guild.members:
            if not getToken(member.id) and (member.id in memberlist):
                people.append(member.name)

        await message.channel.send(", ".join(people))
