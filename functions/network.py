import asyncio
import time

import aiohttp

from functions.database import getToken, getTokenExpiry
from oauth import refresh_token
from static.config import BUNGIE_TOKEN

bungieAPI_URL = "https://www.bungie.net/Platform"
headers = {'X-API-Key': BUNGIE_TOKEN}


async def getJSONfromURL(requestURL, headers=headers, params={}):
    """ Grabs JSON from the specified URL (no oauth)"""
    no_jar = aiohttp.DummyCookieJar()
    async with aiohttp.ClientSession(cookie_jar=no_jar) as session:
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

    # handle and return working token
    ret = await handleAndReturnToken(discordID)
    if ret["result"]:
        token = ret["result"]
    else:
        return ret

    headers = {
        'Authorization': f'Bearer {token}',
        'x-api-key': BUNGIE_TOKEN,
        'Accept': 'application/json'
    }

    no_jar = aiohttp.DummyCookieJar()
    async with aiohttp.ClientSession(cookie_jar=no_jar) as session:
        # abort after 5 tries
        for i in range(5):
            async with session.get(url=requestURL, headers=headers) as r:
                # ok
                if r.status == 200:
                    res = await r.json()
                    return {'result': res, 'error': None}

                # handling any errors if not ok
                else:
                    if await errorCodeHandling(requestURL, r):
                        return {'result': None, 'error': f"Status Code <{r.status}>"}

        print('Request failed 5 times, aborting')
        try:
            error = await r.json()
            msg = f"""Didn't get a valid response. Bungie returned status {r.status}: \n`ErrorCode - {error["ErrorCode"]} \nErrorStatus - {error["ErrorStatus"]} \nMessage - {error["Message"]}`"""
        except:
            msg = "Bungie is doing wierd stuff right now or there is a big error in my programming, the first is definitely more likely. Try again in a sec."

        return {'result': None, 'error': msg}


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

    # handle and return working token
    ret = await handleAndReturnToken(discordID)
    if ret["result"]:
        token = ret["result"]
    else:
        return ret

    headers = {
        'Authorization': f'Bearer {token}',
        'x-api-key': BUNGIE_TOKEN,
        'Accept': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        # abort after 5 tries
        for i in range(5):
            async with session.post(url=postURL, json=data, headers=headers, allow_redirects=False) as r:
                # ok
                if r.status == 200:
                    res = await r.json()
                    return {'result': res, 'error': None}

                # handling any errors if not ok
                else:
                    if await errorCodeHandling(postURL, r):
                        return {'result': None, 'error': f"Status Code <{r.status}>"}

        print('Request failed 5 times, aborting')
        try:
            error = await r.json()
            msg = f"""Didn't get a valid response. Bungie returned status {r.status}: \n`ErrorCode - {error["ErrorCode"]} \nErrorStatus - {error["ErrorStatus"]} \nMessage - {error["Message"]}`"""
        except:
            msg = "Bungie is doing wierd stuff right now or there is a big error in my programming, the first is definitely more likely. Try again in a sec."

        return {'result': None, 'error': msg}

# if this returns True, None should be return by the caller. If it returns False, it should try again
async def errorCodeHandling(requestURL, r):
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
        res = await r.json()
        error = res["ErrorStatus"]
        # we we are getting throttled
        if error == "PerEndpointRequestThrottleExceeded":
            await asyncio.sleep(res["ThrottleSeconds"])

        # if user doesn't have that item
        elif error == "DestinyItemNotFound":
            print("User doesn't have that item, aborting")
            return True

        else:
            print(f'Bad request for {requestURL}. Returned error {error}:')
            print(res)

    # bungo is ded
    elif r.status == 503:
        print(f'Server is overloaded, waiting 10s and then trying again')
        await asyncio.sleep(10)
    # rate limited
    elif r.status == 429:
        print(f"Getting rate limited, waiting 2s and trying again")
        await asyncio.sleep(2)

    else:
        print(f"Failed with code {r.status}. Waiting 1s and trying again")
        await asyncio.sleep(1)

    return False

async def handleAndReturnToken(discordID):
    token = getToken(discordID)
    if not token:
        print(f'Token not found for discordID {discordID}')
        return {
            'result': None,
            'error': 'User has not registered'
        }

    # refresh token if expired
    expiry = getTokenExpiry(discordID)
    if not expiry:
        print(f'Expiry Dates not found for discordID {discordID}, refreshing tokens')
        return {
            'result': None,
            'error': 'User tokens have no expiry date'
        }

    t = int(time.time())

    # check refresh token first, since they need to re-register otherwise
    if t > expiry[1]:
        print(f'Expiry Dates for refreshed token passed for discordID {discordID}. Needs to re-register')
        return {
            'result': None,
            'error': 'Registration is outdated, please re-register using `!registerdesc`'
        }

    # refresh token if outdated
    elif t > expiry[0]:
        print(f"Refreshing token for discordID {discordID}")
        token = await getFreshToken(discordID)
        if not token:

            return {
                'result': None,
                'error': 'Token refresh failed'
            }

    return {
            'result': token,
            'error': ''
        }


async def getFreshToken(discordID):
    return await refresh_token(discordID)

