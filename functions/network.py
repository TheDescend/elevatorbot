from static.config import BUNGIE_TOKEN
from oauth import refresh_token
from functions.database import getToken

import requests
import time

import logging
import http.client

bungieAPI_URL = "https://www.bungie.net/Platform"
PARAMS = {'X-API-Key': BUNGIE_TOKEN}
session = requests.Session()

#HTTP debugging, set to True to enable
if False:
    http.client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    req_log = logging.getLogger('requests.packages.urllib3')
    req_log.setLevel(logging.DEBUG)
    req_log.propagate = True

def getJSONfromURL(requestURL):
    """ Grabs JSON from the specified URL (no oauth)"""
    for i in range(5):
        # doesn't sleep on first run, but after - to relax the servers
        time.sleep(i)
        try:
            if 'None' in requestURL:
                break
            r = session.get(url=requestURL, headers=PARAMS)
        except Exception as e:
            print('Exception was caught: ' + repr(e))
            continue
        if r.status_code == 200:
            returnval = r.json()
            return returnval
        elif r.status_code == 400:
            #malformated URL, e.g. wrong subsystem for bungie
            return None
        elif r.status_code == 404:
            print('no stats found')
            return None
        elif r.status_code == 500:
            print(f'bad request for {requestURL}')
        elif r.status_code == 503:
            print(f'bungo is ded')
            return None
        else:
            print('failed with code ' + str(r.status_code) + ' servers might be busy')
    print('request failed 3 times') 
    return None

#https://bungie-net.github.io/multi/operation_get_Destiny2-GetProfile.html
def getComponentInfoAsJSON(playerID, components): 
    """ Returns certain profile informations, depending on components specified """
    for systemid in [3,2,1,4,5,10,254]: #checking steam, ps, xbox, blizzard, *weird_ones
        url = bungieAPI_URL + '/Destiny2/{}/Profile/{}?components={}'.format(systemid, playerID, components)
        playerData = getJSONfromURL(url)
        if playerData is not None:
            return playerData
    print('getting playerinfo failed')
    return None



def getFreshToken(discordID):
    refresh_token(discordID)
    return getToken(discordID)


def getJSONwithToken(url, discordID):
    """ Takes url and discordID, returns JSON """

    token = getToken(discordID)
    if not token:
        return None
    # print(f'using {token}')
    headers = {'Authorization': f'Bearer {token}', 'x-api-key': BUNGIE_TOKEN, 'Accept': 'application/json'}
    r = session.get(url, headers=headers)

    if b'Unauthorized' in r.content:
        print('xml 401 found')
        refresh_token(discordID)
        return getJSONwithToken(url, discordID)

    res = r.json()

    if int(res['ErrorCode']) == 401:
        print('json 401 found')
        refresh_token(discordID)
        return getJSONwithToken(url, discordID)

    if int(res['ErrorCode']) != 1:
        print(url)
        print(headers)
        print(f'ErrorCode is not 1, but {res["ErrorCode"]}')
        return None

    # print(f'Tokenfunction returned {res}')
    return res