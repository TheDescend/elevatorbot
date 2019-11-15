
from commands.base_command  import BaseCommand
from functions              import getNameToHashMapByClanid
from fuzzywuzzy             import fuzz

import requests, config

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
        username = message.author.display_name
        if len(params) == 1:
            username = str(params[0])
        PARAMS = {'X-API-Key':config.BUNGIE_TOKEN}


        maxName = None
        maxProb = 0
        for ingameName in memberMap.keys():
            #prob = fuzz.ratio(username, ingameName)
            uqprob = fuzz.UQRatio(username, ingameName)
            #uwprob = fuzz.UWRatio(username, ingameName)
            if uqprob > maxProb:
                #strng = '{} prob, '.format(prob) + " " + '{} prob, '.format(uqprob) + '{} prob '.format(uwprob)+ username + ' = ' + ingameName
                #await message.channel.send(strng)
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


        