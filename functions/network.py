from static.config import BUNGIE_TOKEN
from oauth import refresh_token
from functions.database import getToken

import aiohttp
import asyncio


bungieAPI_URL = "https://www.bungie.net/Platform"
headers = {'X-API-Key': BUNGIE_TOKEN}


async def getJSONfromURL(requestURL, headers=headers, params={}):
    """ Grabs JSON from the specified URL (no oauth)"""

    async with aiohttp.ClientSession() as session:
        # abort after 5 tries
        for i in range(5):
            async with session.get(url=requestURL, headers=headers, params=params) as r:
                # ok
                if r.status == 200:
                    return await r.json()
                # generic bad request, such as wrong format
                elif r.status == 400:
                    print(f'Generic bad request for {requestURL}')
                    return None
                # not found
                elif r.status == 404:
                    print(f'No stats found for {requestURL}')
                    return None
                # Internal server error
                elif r.status == 500:
                    print(f'Bad request for {requestURL}')
                # bungo is ded
                elif r.status == 503:
                    print(f'Server is overloaded, waiting 10s and then trying again')
                    await asyncio.sleep(10)
                # rate limited
                elif r.status == 429:
                    print(f"Getting rate limited, waiting 1s and trying again")
                    await asyncio.sleep(1)

                else:
                    print(f"Failed with code {r.status}. Waiting 1s and trying again")
                    await asyncio.sleep(1)

        print('Request failed 5 times, aborting')
        return None

async def getJSONwithToken(requestURL, discordID):
    """ Takes url and discordID, returns dict with [token] = JSON, otherwise [error] has a errormessage """

    token = getToken(discordID)
    if not token:
        print(f'Token not found for discordID {discordID}')
        return {
            'result': None,
            'error': 'User has not registered'
        }

    headers = {'Authorization': f'Bearer {token}', 'x-api-key': BUNGIE_TOKEN, 'Accept': 'application/json'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url=requestURL, headers=headers) as r:
            res = None

            # ok
            if r.status == 200:
                res = await r.json()
            elif b'Unauthorized' in r.content:
                print('xml 401 found')
                await refresh_token(discordID)
                return await getJSONwithToken(requestURL, discordID)
            elif r.status == 500:
                print('bungierequest gave 500')
                return {'result': None, 'error':'Bungie seems to be offline'}

            if res:
                if int(res['ErrorCode']) == 401:
                    print('json 401 found')
                    await refresh_token(discordID)
                    return await getJSONwithToken(requestURL, discordID)

                if int(res['ErrorCode']) != 1:
                    print(requestURL)
                    print(headers)
                    print(f'ErrorCode is not 1, but {res["ErrorCode"]}')
                    return {'result': None, 'error': f'You encountered error {res["ErrorCode"]}, please inform <@171650677607497730>'}

                # print(f'Tokenfunction returned {res}')
                return {'result': res, 'error': None}


# https://bungie-net.github.io/multi/operation_get_Destiny2-GetProfile.html
async def getComponentInfoAsJSON(playerID, components):
    """ Returns certain profile information, depending on components specified """

    # checking steam, ps, xbox, blizzard, *weird_ones
    for systemid in [3,2,1,4,5,10,254]:
        url = bungieAPI_URL + '/Destiny2/{}/Profile/{}?components={}'.format(systemid, playerID, components)
        playerData = await getJSONfromURL(url)
        if playerData is not None:
            return playerData

    print('Getting playerinfo failed')
    return None


async def getFreshToken(discordID):
    await refresh_token(discordID)
    return getToken(discordID)




""" old code """
# def getJSONfromURL(requestURL):
#     """ Grabs JSON from the specified URL (no oauth)"""
#     for i in range(5):
#         # doesn't sleep on first run, but after - to relax the servers
#         time.sleep(i)
#         try:
#             if 'None' in requestURL:
#                 break
#             r = session.get(url=requestURL, headers=PARAMS)
#         except Exception as e:
#             print('Exception was caught: ' + repr(e))
#             continue
#         if r.status_code == 200:
#             returnval = r.json()
#             return returnval
#         elif r.status_code == 400:
#             #malformated URL, e.g. wrong subsystem for bungie
#             return None
#         elif r.status_code == 404:
#             print('no stats found')
#             return None
#         elif r.status_code == 500:
#             print(f'bad request for {requestURL}')
#         elif r.status_code == 503:
#             print(f'bungo is ded')
#             return None
#         else:
#             print('failed with code ' + str(r.status_code) + ' servers might be busy')
#     print('request failed 3 times')
#     return None
#
# #https://bungie-net.github.io/multi/operation_get_Destiny2-GetProfile.html
# def getComponentInfoAsJSON(playerID, components):
#     """ Returns certain profile informations, depending on components specified """
#     for systemid in [3,2,1,4,5,10,254]: #checking steam, ps, xbox, blizzard, *weird_ones
#         url = bungieAPI_URL + '/Destiny2/{}/Profile/{}?components={}'.format(systemid, playerID, components)
#         playerData = getJSONfromURL(url)
#         if playerData is not None:
#             return playerData
#     print('getting playerinfo failed')
#     return None
#
#
#
# def getFreshToken(discordID):
#     refresh_token(discordID)
#     return getToken(discordID)
#
#
# def getJSONwithToken(url, discordID):
#     """ Takes url and discordID, returns dict with [token] = JSON, otherwise [error] has a errormessage """
#
#     token = getToken(discordID)
#     if not token:
#         print(f'token not found for discordID {discordID}')
#         return {'result': None, 'error':'User has not registered'}
#     #print(f'using {token}')
#     headers = {'Authorization': f'Bearer {token}', 'x-api-key': BUNGIE_TOKEN, 'Accept': 'application/json'}
#     r = session.get(url, headers=headers)
#
#     if b'Unauthorized' in r.content:
#         print('xml 401 found')
#         refresh_token(discordID)
#         return getJSONwithToken(url, discordID)
#
#     if int(r.status_code) == 500:
#         print('bungierequest gave 500')
#         return {'result': None, 'error':'Bungie seems to be offline'}
#
#     res = r.json()
#     if int(res['ErrorCode']) == 401:
#         print('json 401 found')
#         refresh_token(discordID)
#         return getJSONwithToken(url, discordID)
#
#     if int(res['ErrorCode']) != 1:
#         print(url)
#         print(headers)
#         print(f'ErrorCode is not 1, but {res["ErrorCode"]}')
#         return {'result': None, 'error': f'You encountered error {res["ErrorCode"]}, please inform <@171650677607497730>'}
#
#     # print(f'Tokenfunction returned {res}')
#     return {'result': res, 'error': None}