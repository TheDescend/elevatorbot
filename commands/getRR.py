
from commands.base_command  import BaseCommand
from functions.dataLoading  import getNameToHashMapByClanid, updateDB
from static.config          import BUNGIE_TOKEN
from static.dict            import clanids
from discord.ext            import commands

from functions.database     import lookupDestinyID, getSystemAndChars
from functions.formating    import embed_message
import re, requests

base_uri = 'https://discordapp.com/api/v7'
memberMap = getNameToHashMapByClanid(list(clanids.keys())[0])
rrsystem = {
    1: 'xb',
    2: 'ps',
    3: 'pc'
}

class RR(BaseCommand):
    def __init__(self):
        description = "get your personal raid.report link"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        PARAMS = {'X-API-Key':BUNGIE_TOKEN}
        username = message.author.nick or message.author.name

        if len(params) == 1:
            ctx = await client.get_context(message)
            try:
                user = await commands.MemberConverter().convert(ctx, params[0])
            except:
                await message.channel.send(embed=embed_message(
                    'Error',
                    f'User not found, make sure the spelling/id is correct'
                ))
                return

            destinyID = lookupDestinyID(user.id)
        else:
            destinyID = lookupDestinyID(message.author.id)
            
        if destinyID:
            syscharlist = getSystemAndChars(destinyID)
            if not syscharlist:
                #get them I guess
                await message.channel.send("Player not yet in db, updating...")
                updateDB(destinyID)
                syscharlist = getSystemAndChars(destinyID)
                if not syscharlist:
                    print(f'{destinyID} is borked')
                    await message.channel.send(embed=embed_message(
                        'Raid Report',
                        f'Invalid DestinyID {destinyID}'
                    ))
            systemID, _ = syscharlist[0]
            await message.channel.send(embed=embed_message(
                'Raid Report',
                f'https://raid.report/{rrsystem[systemID]}/{destinyID}'
            ))
            return
        else:
            await message.channel.send(embed=embed_message(
                'Error',
                'Name needs to be more specific or is not in Clan'
            ))


class DR(BaseCommand):
    def __init__(self):
        description = "get your personal dungeon.report link"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        PARAMS = {'X-API-Key':BUNGIE_TOKEN}
        username = message.author.nick or message.author.name

        if len(params) == 1:
            ctx = await client.get_context(message)
            try:
                user = await commands.MemberConverter().convert(ctx, params[0])
            except:
                await message.channel.send(embed=embed_message(
                    'Error',
                    f'User not found, make sure the spelling/id is correct'
                ))
                return
            username = user.name

            destinyID = lookupDestinyID(user.id)
            if destinyID:
                systemID, _ = getSystemAndChars(destinyID)[0]
                await message.channel.send(embed=embed_message(
                    'Dungeon Report',
                    f'https://dungeon.report/{rrsystem[systemID]}/{destinyID}'
                ))
                return
        else:
            destinyID = lookupDestinyID(message.author.id)
            if destinyID:
                systemID, _ = getSystemAndChars(destinyID)[0]
                await message.channel.send(embed=embed_message(
                    'Dungeon Report',
                    f'https://dungeon.report/{rrsystem[systemID]}/{destinyID}'
                ))
                return

        await message.channel.send(embed=embed_message(
            'Error',
            'Name needs to be more specific or is not in Clan'
        ))
        