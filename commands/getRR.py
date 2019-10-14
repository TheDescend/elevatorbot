
from commands.base_command  import BaseCommand
from utils                  import get_emoji
from random                 import randint
from functions              import getNameToHashMapByClanid
from fuzzywuzzy             import fuzz
#from fuzzywuzzy             import process
#from discord                import *

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


class RR(BaseCommand):
    def __init__(self):
        description = "your personal raidreport"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        username = message.author.display_name
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


class getRR(BaseCommand):
    def __init__(self):
        description = "someone else's raidreport"
        params = ['user']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        username = params[0]
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



        