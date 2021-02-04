import datetime

from commands.base_command import BaseCommand
from events.armorStatsNotifier import ArmorStatsNotifier
from functions.dataLoading import getCharactertypeList, getCharacterList, OUTDATEDgetSystem, getInventoryBucket, \
    updateDB, updateManifest
from functions.dataTransformation import hasCollectible
from functions.database import removeUser, lookupDestinyID, getEverything, updateUser, updateToken, getRefreshToken
from functions.formating import embed_message
from functions.miscFunctions import hasAdminOrDevPermissions
from functions.persistentMessages import botStatus
from oauth import refresh_token
from static.config import BUNGIE_OAUTH

class getDay1Completions(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev]Register with bungie.net"
        params = []
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        # users = getEverything()

        # notokenlist = []

        # for (discordSnowflake, destinyID, serverID, systemID, token, _refresh_token, token_expiry, refresh_token_expiry) in users:
        #     if not token_expiry or not refresh_token_expiry:
        #         if not _refresh_token:
        #             notokenlist.append(str(discordSnowflake))
        #             continue
        #         ret = await refresh_token(discordSnowflake)
                
        #         if ret:
        #             await message.channel.send(f"Updated tokens from discordID {discordSnowflake} destinyID {destinyID}")
        #         else:
        #             await message.channel.send(f"__**Update tokens from discordID {discordSnowflake} destinyID {destinyID} failed**__")
        # broketext = ", ".join(notokenlist)
        # await message.channel.send(f'following users did not have a token to refresh {broketext[:1900]}')
        # await message.channel.send(f'{broketext[1900:]}')
        # await message.channel.send("Done")
        
        userlist = []
        for member in message.guild.members:
            if message.guild.get_role(670384239489056768) in member.roles: #isdescend
                destinyid = lookupDestinyID(member.id)
                if await hasCollectible(destinyid, 2273453972):
                    userlist.append(member.name)
        await message.channel.send(", ".join(userlist))


class updateKigstn(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev]Register with bungie.net"
        params = []
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        a = ArmorStatsNotifier()
        await a.run(client)

