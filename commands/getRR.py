
from commands.base_command  import BaseCommand
from functions              import getNameToHashMapByClanid
from fuzzywuzzy             import fuzz

import requests, config
from functions import getUserMap
import re

base_uri = 'https://discordapp.com/api/v7'
memberMap = getNameToHashMapByClanid(2784110)

class getRRbungo(BaseCommand):
    def __init__(self):
        description = "input bungie.net id to get the raid.report link"
        params = ['bungieID']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        bungieID = int(params[0])
        PARAMS = {'X-API-Key':config.BUNGIE_TOKEN}
        url = 'https://www.bungie.net/platform/User/GetMembershipsById/{}/{}/'.format(bungieID,3)
        r=requests.get(url=url, headers=PARAMS)
        memberships = r.json()['Response']['destinyMemberships']
        for membership in memberships:
            if membership['membershipType'] == 3:
                print('https://raid.report/pc/' + membership['membershipId'])
                await message.channel.send('https://raid.report/pc/' + membership['membershipId'])


class getRRsteam(BaseCommand):
    def __init__(self):
        description = "input steamid to get the raid.report link"
        params = ['steamID']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        steamID = int(params[0])
        PARAMS = {'X-API-Key':config.BUNGIE_TOKEN}
        url = 'https://www.bungie.net/Platform/User/GetMembershipFromHardLinkedCredential/{}/{}/'.format(12,steamID)
        r=requests.get(url=url, headers=PARAMS)
        #print(r.json())
        destinyID = r.json()['Response']['membershipId']
        await message.channel.send('https://raid.report/pc/' + destinyID)

class RR(BaseCommand):
    def __init__(self):
        description = "get the raidreport link"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        PARAMS = {'X-API-Key':config.BUNGIE_TOKEN}
        username = message.author.nick or message.author.name

        if len(params) == 1:
            mentionregex = re.compile(r'<@([A-Za-z0-9]*)>') 
            result = mentionregex.search(params[0]) 
            discordID = None
            if result.group(1):
                discordID = int(result.group(1))
                user = client.get_user(discordID)
                username = user.nick or user.name

                destinyID = getUserMap(discordID)
                if destinyID:
                    await message.channel.send('https://raid.report/pc/' + destinyID)
                    return
            else:
                username = params[0]
        else:
            destinyID = getUserMap(message.author.id)
            if destinyID:
                await message.channel.send('https://raid.report/pc/' + destinyID)
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
            await message.channel.send('Name needs to be more specific or is not in BO Clan')


        