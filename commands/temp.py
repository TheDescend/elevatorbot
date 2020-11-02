from commands.base_command import BaseCommand
from functions.dataLoading import getCharactertypeList, getCharacterList, OUTDATEDgetSystem
from functions.database import removeUser, lookupDestinyID, getEverything, updateUser, updateToken
from functions.formating import embed_message
from functions.roles import hasAdminOrDevPermissions
from oauth import refresh_token
from static.config import BUNGIE_OAUTH


class fixMembershipTypes(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev]Register with bungie.net"
        params = []
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        users = getEverything()

        for user in users:
            if not user[3]:
                membID = (await OUTDATEDgetSystem(user[1]))
                if not membID:
                    await message.channel.send(f"__**No membershipType found for discordID {user[0]} destinyID {user[1]}**__")
                else:
                    updateUser(user[0], user[1], membID)
                    await message.channel.send(f"Update discordID {user[0]} destinyID {user[1]} with membershipType {membID}")

        await message.channel.send("Done")

class fixTokenExpiry(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev]Register with bungie.net"
        params = []
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        users = getEverything()

        for user in users:
            if not user[6] or not user[7]:
                ret = await refresh_token(user[0])
                if ret:
                    await message.channel.send(f"Update tokens from discordID {user[0]} destinyID {user[1]}")
                else:
                    await message.channel.send(f"__**Update tokens from discordID {user[0]} destinyID {user[1]} failed**__")

        await message.channel.send("Done")

