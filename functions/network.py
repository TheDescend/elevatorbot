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

                # handling any errors if not ok
                if await errorCodeHandling(requestURL, r):
                    return None

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

    headers = {
        'Authorization': f'Bearer {token}',
        'x-api-key': BUNGIE_TOKEN,
        'Accept': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        # abort after 5 tries
        for i in range(5):
            async with session.get(url=requestURL, headers=headers) as r:
                res = None

                # ok
                if r.status == 200:
                    res = await r.json()

                # handling any errors if not ok
                else:
                    if await errorCodeHandling(requestURL, r, discordID):
                        return {'result': None, 'error': f"Status Code <{r.status}>"}

                if res:
                    if int(res['ErrorCode']) == 401:
                        print('json 401 found')
                        await refresh_token(discordID)

                    if int(res['ErrorCode']) != 1:
                        print(requestURL)
                        print(headers)
                        print(f'ErrorCode is not 1, but {res["ErrorCode"]}')
                        return {'result': None, 'error': f'You encountered error {res["ErrorCode"]}, please inform <@171650677607497730>'}

                    # print(f'Tokenfunction returned {res}')
                    return {'result': res, 'error': None}

        print('Request failed 5 times, aborting')
        return {'result': None, 'error': "Didn't get a valid response from Bungie. Servers might be down, try again later."}


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


async def postJSONtoBungie(postURL, data, discordID):
    """ Post info to bungie """

    token = getToken(discordID)
    if not token:
        print(f'Token not found for discordID {discordID}')
        return {
            'result': None,
            'error': 'User has not registered'
        }

    headers = {
        'Authorization': f'Bearer {token}',
        'x-api-key': BUNGIE_TOKEN,
        'Accept': 'application/json'}

    async with aiohttp.ClientSession() as session:
        # abort after 5 tries
        for i in range(5):
            async with session.post(url=postURL, json=data, headers=headers, allow_redirects=False) as r:
                res = None
                print(await r.read())
                # ok
                if r.status == 200:
                    res = await r.json()

                # handling any errors if not ok
                else:
                    if await errorCodeHandling(postURL, r, discordID):
                        return {'result': None, 'error': f"Status Code <{r.status}>"}

                if res:
                    if int(res['ErrorCode']) == 401:
                        print('json 401 found')
                        print(f'Refreshing token for discordID {discordID}')
                        return await postJSONtoBungie(postURL, data, discordID)

                    if int(res['ErrorCode']) != 1:
                        print(postURL)
                        print(headers)
                        print(f'ErrorCode is not 1, but {res["ErrorCode"]}')
                        return {'result': None, 'error': f'You encountered error {res["ErrorCode"]}, please inform <@171650677607497730>'}

                    # print(f'Tokenfunction returned {res}')
                    return {'result': res, 'error': None}
            asyncio.sleep(2)

        print('Request failed 5 times, aborting')
        try:
            error = await r.json()
            msg = f"""Didn't get a valid response. Bungie returned status {r.status}: \n`ErrorCode - {error["ErrorCode"]} \nErrorStatus - {error["ErrorStatus"]} \nMessage - {error["Message"]}`"""
        except:
            msg = "Bungie is doing wierd stuff right now or there is a big error in my programming, the first is definitely more likely. Try again in a sec."

        return {'result': None, 'error': msg}

# if this returns True, None should be return by the caller. If it returns False, it should try again
async def errorCodeHandling(requestURL, r, discordID=None):
    # refreshing token if outdated. Only relevant if used with oauth
    if discordID:
        result = await r.read()
        if b'Unauthorized' in result:
            print(result)
            print('Token outdated, refreshing...')
            await refresh_token(discordID)
            return False

    # generic bad request, such as wrong format
    if r.status == 400:
        print(f'Generic bad request for {requestURL}')
        return True
    # not found
    elif r.status == 404:
        print(f'No stats found for {requestURL}')
        return True
    # Internal server error
    elif r.status == 500:
        print(f'Bad request for {requestURL}. Returned:')
        print(await r.read())
        # bungo is ded
    elif r.status == 503:
        print(f'Server is overloaded, waiting 10s and then trying again')
        await asyncio.sleep(10)
    # rate limited
    elif r.status == 429:
        print(f"Getting rate limited, waiting 1s and trying again")
        await asyncio.sleep(1)

    print(f"Failed with code {r.status}. Waiting 1s and trying again")
    await asyncio.sleep(1)
    return False


async def getFreshToken(discordID):
    await refresh_token(discordID)
    return getToken(discordID)
