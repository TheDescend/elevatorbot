from static.config import BUNGIE_TOKEN
import requests

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
    for _ in range(3):
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
            print('failed with code ' + str(r.status_code) + (', because servers are busy' if ('ErrorCode' in r.json() and r.json()['ErrorCode']==1672) else ''))
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