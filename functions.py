import requests

import config
from dict import platform,requirementHashes

baseURL = "https://www.bungie.net/Platform"
PARAMS = {'X-API-Key': config.key}

systemdict = {}
jsondict = {}
def getJSONfromURL(requestURL, baseURL=baseURL, console=False, playerid=None):
    if requestURL in jsondict:
        return jsondict[requestURL]
    r = requests.get(url=baseURL + str(requestURL), headers=PARAMS)
    if r.status_code == 200:
        jsondict[requestURL] = r.json()
        return r.json()
    elif r.status_code == 400:
        if console:
            return None
        print(requestURL + ' not on steam')
        for i in [1,2,4,5,10,254]:
            console = getJSONfromURL('/Destiny2/' + str(i) + requestURL[11:], baseURL=baseURL, console=True, playerid = playerid)
            if console is not None:
                print('found on ' + platform.get(i))
                systemdict[playerid] = i
                jsondict[requestURL] = console
                return console
        return None
    else:
        print('request for ' + baseURL + requestURL + ' failed with code ' + str(r.status_code))
    return r.json()

def playerHasCollectible(playerid, cHash, systemid=3):
    if playerid in systemdict:
        systemid = systemdict[playerid]
    userCollectibles = getJSONfromURL('/Destiny2/{}/Profile/{}?components=800'.format(systemid, playerid), playerid=playerid)
    collectibles = userCollectibles['Response']['profileCollectibles']['data']['collectibles']
    return collectibles[cHash]['state'] == 0

playerActivities = {}
def getClearCount(playerid, activityHashes):
    if not str(playerid) in playerActivities.keys():
        rrBaseURL = 'https://b9bv2wd97h.execute-api.us-west-2.amazonaws.com/prod/api/player/'
        requestURL = playerid
        profileInfo = getJSONfromURL(requestURL, baseURL=rrBaseURL, playerid=playerid)
        playerActivities[str(playerid)] = profileInfo['response']['activities'] # list of dicts that contain activityHash and values

    counter = 0
    for activityInfo in playerActivities[str(playerid)]:
        if str(activityInfo['activityHash']) in activityHashes:
            counter += int(activityInfo['values']['fullClears'])
            print('hi')
    return counter

def flawlessList(playerid):
    rrBaseURL = 'https://b9bv2wd97h.execute-api.us-west-2.amazonaws.com/prod/api/player/'
    requestURL = playerid
    profileInfo = getJSONfromURL(requestURL, baseURL=rrBaseURL, playerid=playerid)
    activities = profileInfo['response']['activities']

    flawlessL = []
    for raid in activities:
        if 'flawlessDetails' in raid['values'].keys():
            flawlessL.append(str(raid['activityHash']))
    return flawlessL

def getTriumphsJSON(playerid, system=3):
    if playerid in systemdict:
        system = systemdict[playerid]
    requestURL = "/Destiny2/{}/Profile/{}?components=900".format(system, playerid) 
    achJSON = getJSONfromURL(requestURL, playerid=playerid)
    return achJSON['Response']['profileRecords']['data']['records']

def playerHasTriumph(playerid, recordHash):
    status = True
    triumphs = getTriumphsJSON(playerid)
    for part in triumphs[recordHash]['objectives']:
        status &= (str(part['complete']) == 'True')
    return status

def playerHasClears(playerid, n, raidHashes):
    count = 0
    for h in raidHashes:
        count += getClearCount(playerid, h)
    return count >= n

def playerHasFlawless(playerid, raidHashes):
    flawlessL = flawlessList(playerid)
    for r in raidHashes:
        if r in flawlessL:
            return True
    return False

def playerHasRole(playerid, role, year):
    roledata = requirementHashes[year][role]
    if not 'requirements' in roledata:
        print('malformatted requirementHashes')
        return None
    for req in roledata['requirements']:
        if req == 'clears':
            creq = roledata['clears']
            for raid in creq:
                requiredN = raid['count']
                if not playerHasClears(playerid, requiredN, raid['actHashes']):
                    return False
        elif req == 'flawless':
            if not playerHasFlawless(playerid, roledata['flawless']):
                return False
        elif req == 'collectibles':
            for collectible in roledata['collectibles']:
                if not playerHasCollectible(playerid, collectible):
                    return False
        elif req == 'records':
            for recordHash in roledata['records']:
                if not playerHasTriumph(playerid, recordHash):
                    return False
    return True

def getNameToHashMapByClanid(clanid):
    requestURL = "/GroupV2/{}/members/".format(clanid) #bloodoak memberlist
    memberJSON = getJSONfromURL(requestURL)
    memberlist = memberJSON['Response']['results']
    memberids  = dict()
    for member in memberlist:
        memberids[member['destinyUserInfo']['LastSeenDisplayName']] = member['destinyUserInfo']['membershipId']
    return memberids