
from commands.base_command  import BaseCommand
from functions              import getNameToHashMapByClanid
from fuzzywuzzy             import fuzz

import requests, config
from functions import getUserMap
import re

base_uri = 'https://discordapp.com/api/v7'
memberMap = getNameToHashMapByClanid(2784110)

class RR(BaseCommand):
    def __init__(self):
        description = "get your personal raid.report link"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        PARAMS = {'X-API-Key':config.BUNGIE_TOKEN}
        username = message.author.nick or message.author.name

        if len(params) == 1:
            mentionregex = re.compile(r'<@!?([0-9]*)>') 
            result = mentionregex.search(params[0]) 
            discordID = None
            if not result:
                await message.channel.send(f'invalid argument, please ping someone or type nothing for yourself')
                return
            if result.group(1):
                discordID = int(result.group(1))
                user = client.get_user(discordID)
                username = user.name

                destinyID = getUserMap(discordID)
                if destinyID:
                    await message.channel.send(f'https://raid.report/pc/{destinyID}')
                    return
        else:
            destinyID = getUserMap(message.author.id)
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


        