import asyncio
import aiohttp

import random
import time
from datetime import datetime


from static.config import B64_SECRET, BUNGIE_TOKEN

from functions.database import (getRefreshToken, getToken, getTokenExpiry,
                                lookupDestinyID, updateToken)

bungieAPI_URL = "https://www.bungie.net/Platform"
headers = {'X-API-Key': BUNGIE_TOKEN}

class ConnectionProvider:

    def __init__(self):
        self.bungieSession = None
        self.otherSession = None

    def getSession(self, url):
        if 'bungie' in url:
            if not self.bungieSession or self.bungieSession.closed:
                self.bungieSession = aiohttp.ClientSession(connector=aiohttp.TCPConnector(keepalive_timeout=100, limit=10))
            return self.bungieSession
        else:
            if not self.otherSession or self.otherSession.closed:
                self.otherSession = aiohttp.ClientSession()
            return self.otherSession

connProvider = ConnectionProvider()

class RateLimiter:
    """
    Gives out x tokens for network operations every y seconds
    Adapted from https://gist.github.com/pquentin/5d8f5408cdad73e589d85ba509091741
    """
    RATE = 20               # how many requests per second - bungie allows 20/s
    MAX_TOKENS = 240        # how many requests can we save up - bungie limits after 250 in 10s, so will put that to 240

    def __init__(self):
        self.tokens = self.MAX_TOKENS
        self.updated_at = time.monotonic()

    async def wait_for_token(self):
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(0.1)
        self.tokens -= 1

    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.RATE
        if self.tokens + new_tokens >= 1:
            self.tokens = min(self.tokens + new_tokens, self.MAX_TOKENS)
            self.updated_at = now


# the limiter object which is gonna get used everywhere
limiter = RateLimiter()


async def getJSONfromURL(requestURL, headers=headers, params={}):
    """ Grabs JSON from the specified URL (no oauth)"""

    async with aiohttp.ClientSession() as session:
        # abort after 5 tries
        for i in range(10):
            # wait for a token from the rate limiter
            async with asyncio.Lock():
                await limiter.wait_for_token()

            try:
                async with session.get(url=requestURL, headers=headers, params=params, timeout=5) as r:
                    if 'application/json' not in r.headers['Content-Type']: #might be application/json; charset=utf-8
                        print(f'Wrong content type {r.headers["Content-Type"]}! {r.status}: {r.reason})')
                        if r.status == 200:
                            print(await r.text())
                        await asyncio.sleep(3)
                        continue
                    try:
                        res = await r.json()
                    except aiohttp.client_exceptions.ClientPayloadError:
                        print('Payload error, retrying...')
                        continue
                    except aiohttp.client_exceptions.ContentTypeError:
                        print('Content tpye error, retrying...')
                        continue

                    # ok
                    if r.status == 200:
                        return res

                    # handling any errors if not ok
                    if await errorCodeHandling(requestURL, r, res):
                        return None
            except asyncio.exceptions.TimeoutError:
                    print('Timeout error, retrying...')
                    await asyncio.sleep(random.randrange(2,6))
                    continue

        print(f'Request failed 10 times, aborting {requestURL}')
        return None

async def refresh_token(discordID):
    url = 'https://www.bungie.net/platform/app/oauth/token/'
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'authorization': 'Basic ' + str(B64_SECRET)
    }
    refresh_token = getRefreshToken(discordID)
    if not refresh_token:
        return None

    destinyID = lookupDestinyID(discordID)

    data = {"grant_type":"refresh_token", "refresh_token": str(refresh_token)}

    async with aiohttp.ClientSession() as session:
        for i in range(5):
            t = int(time.time())
            async with session.post(url, data=data, headers=headers, allow_redirects=False) as r:
                if r.status == 200:
                    data = await r.json()
                    access_token = data['access_token']
                    refresh_token = data['refresh_token']
                    token_expiry = t + data['expires_in']
                    refresh_token_expiry = t + data['refresh_expires_in']
                    updateToken(destinyID, discordID, access_token, refresh_token, token_expiry, refresh_token_expiry)
                    return access_token
                else:
                    if data["error_description"] == "ApplicationTokenKeyIdDoesNotExist":
                        print(f"Can't update token for destinyID {destinyID} - refresh token is outdated")
                        return None
                    print(f"Refreshing Token failed with code {r.status} . Waiting 1s and trying again")
                    print(await r.read(), '\n')
                    await asyncio.sleep(1)

    print(f"Refreshing Token failed with code {r.status}. Failed 5 times, aborting")
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
        for i in range(10):
            # wait for a token from the rate limiter
            async with asyncio.Lock():
                await limiter.wait_for_token()

            async with session.get(url=requestURL, headers=headers) as r:
                if 'application/json' not in r.headers['Content-Type']: #might be application/json; charset=utf-8
                    #print(await r.text())
                    print(f'Wrong content type! {r.status}: {r.reason})')
                    continue
                res = await r.json()

                # ok
                if r.status == 200:
                    return {'result': res, 'error': None}

                # handling any errors if not ok
                else:
                    if await errorCodeHandling(requestURL, r, res):
                        return {'result': None, 'error': f"Status Code <{r.status}>"}
                    if res["ErrorStatus"] == "PerEndpointRequestThrottleExceeded":
                        return await getJSONwithToken(requestURL, discordID)

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
    ret = await handleAndReturnToken(discordID) #iS FIXED AS ONE OF THE CLANS ADMINS
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
        # abort after 10 tries
        for i in range(10):
            # wait for a token from the rate limiter
            async with asyncio.Lock():
                await limiter.wait_for_token()

            async with session.post(url=postURL, json=data, headers=headers, allow_redirects=False) as r:
                if 'application/json' not in r.headers['Content-Type']: #might be application/json; charset=utf-8
                    #print(await r.text())
                    print(f'Wrong content type! {r.status}: {r.reason})')
                    continue
                res = await r.json()

                # ok
                if r.status == 200:
                    return {'result': res, 'error': None}

                # handling any errors if not ok
                else:
                    if await errorCodeHandling(postURL, r, res):
                        return {'result': None, 'error': f"Status Code <{r.status}>"}
                    if res["ErrorStatus"] == "PerEndpointRequestThrottleExceeded":
                        return await postJSONtoBungie(postURL, data, discordID)

        print('Request failed 5 times, aborting')
        try:
            error = await r.json()
            msg = f"""Didn't get a valid response. Bungie returned status {r.status}: \n`ErrorCode - {error["ErrorCode"]} \nErrorStatus - {error["ErrorStatus"]} \nMessage - {error["Message"]}`"""
        except:
            msg = "Bungie is doing wierd stuff right now or there is a big error in my programming, the first is definitely more likely. Try again in a sec."

        return {'result': None, 'error': msg}

# if this returns True, None should be return by the caller. If it returns False, it should try again
async def errorCodeHandling(requestURL, r, res):
    # generic bad request, such as wrong format
    if r.status == 400:
        #network.log
        #print(f'Generic bad request for {requestURL}')
        return True
    # not found
    elif r.status == 404:
        print(f'No stats found for {requestURL}')
        return True
    # Internal server error
    elif r.status == 500:
        error = res["ErrorStatus"]
        # we we are getting throttled
        if error == "PerEndpointRequestThrottleExceeded" or error == "DestinyDirectBabelClientTimeout":
            print(f"Getting throtteled, waiting {res['ThrottleSeconds'] or 'for Babel'}")
            await asyncio.sleep(res["ThrottleSeconds"] + random.randrange(1, 3))

        # if user doesn't have that item
        elif error == "DestinyItemNotFound":
            print("User doesn't have that item, aborting")
            return True
        elif error == "DestinyPrivacyRestriction":
            print("User has private Profile")
            return True
        elif error == "DestinyDirectBabelClientTimeout":
            print("Getting timouts <DestinyDirectBabelClientTimeout>, waiting 60s and trying again")
            await asyncio.sleep(60)
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
        print(f'Expiry Dates for refreshed token passed ({datetime.fromtimestamp(expiry[1]).strftime("%d/%m/%Y")}) for discordID {discordID}. Needs to re-register')
        return {
            'result': None,
            'error': 'Registration is outdated, please re-register using `!registerdesc`'
        }

    # refresh token if outdated
    elif t > expiry[0]:
        print(f'Refreshing token for discordID {discordID}, expired  ({datetime.fromtimestamp(expiry[0]).strftime("%d/%m/%Y")})')
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

