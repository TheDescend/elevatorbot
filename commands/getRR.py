
from commands.base_command  import BaseCommand
from functions.dataLoading  import getNameToHashMapByClanid
from static.config          import BUNGIE_TOKEN
from static.dict            import clanids
from discord.ext            import commands

from fuzzywuzzy             import fuzz
from functions.database     import lookupDestinyID
import re, requests

base_uri = 'https://discordapp.com/api/v7'
memberMap = getNameToHashMapByClanid(list(clanids.keys())[0])

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
                await message.channel.send('User not found, make sure the spelling/id is correct')
                return
            username = user.name

            destinyID = lookupDestinyID(user.id)
            if destinyID:
                await message.channel.send(f'https://raid.report/pc/{destinyID}')
                return
        else:
            destinyID = lookupDestinyID(message.author.id)
            if destinyID:
                await message.channel.send(f'https://raid.report/pc/{destinyID}')
                return

        maxName = None
        maxProb = 0
        for ingameName in memberMap.keys():
            uqprob = fuzz.UQRatio(username, ingameName)
            if uqprob > maxProb:
                maxProb = uqprob
                maxName = ingameName
        if maxName:
            async with message.channel.typing():
                userid = memberMap[maxName]
                url = 'https://www.bungie.net/platform/User/GetMembershipsById/{}/{}/'.format(userid,3)
                r=requests.get(url=url, headers=PARAMS)
                memberships = r.json()['Response']['destinyMemberships']
                for membership in memberships:
                    if membership['membershipType'] == 3:
                        print('https://raid.report/pc/' + membership['membershipId'])
                        await message.channel.send('https://raid.report/pc/' + membership['membershipId'])
        else:
            await message.channel.send('Name needs to be more specific or is not in Clan')


        