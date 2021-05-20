from commands.base_command import BaseCommand
from functions.authfunctions import getSpiderMaterials
from functions.dataLoading import getCharacterList
from database.database import lookupDestinyID
from functions.miscFunctions import hasMentionPermission

# has been slashified
class spoder(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Gives the spoders inventory"
        topic = "Destiny"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        # check perm for other user mention, otherwise abort
        if not (await hasMentionPermission(message, mentioned_user)):
            return

        discordID = mentioned_user.id
        destinyID = lookupDestinyID(discordID)
        anyCharID = (await getCharacterList(destinyID))[1][0]

        async with message.channel.typing():
            materialtext = await getSpiderMaterials(discordID, destinyID, anyCharID)
            if 'embed' in materialtext:
                await message.reply(embed=materialtext['embed'])
            elif materialtext['result']:
                await message.reply(materialtext['result'])
            else:
                await message.channel.send(materialtext['error'])
