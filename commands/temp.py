from commands.base_command  import BaseCommand
from functions.database import lookupDestinyID, updateUser, lookupSystem, getToken
from functions.roles import hasAdminOrDevPermissions
from functions.network import refresh_token

""" Temp commands which should be deleted after a bit """


class addMembershipType(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] gets expiry dates for every user"
        topic = "Registration"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        if not await hasAdminOrDevPermissions(message):
            return
        async for member in message.guild.fetch_members(limit=None):
            destinyID = lookupDestinyID(member.id)
            if destinyID:
                membershipType = lookupSystem(destinyID)
                updateUser(member.id, destinyID, membershipType)

        await message.channel.send("Done!")



class addExpiryDates(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] sets membership type for every user"
        topic = "Registration"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        if not await hasAdminOrDevPermissions(message):
            return

        async for member in message.guild.fetch_members(limit=None):
            destinyID = lookupDestinyID(member.id)
            if destinyID:
                if getToken(member.id):
                    _ = refresh_token(member.id)

        await message.channel.send("Done!")