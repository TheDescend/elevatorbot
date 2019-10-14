import requests

import config
from dict import platform,requirementHashes

bungieAPI_URL = "https://www.bungie.net/Platform"
PARAMS = {'X-API-Key': config.BUNGIE_TOKEN}

jsonByURL = {}
def getJSONfromURL(requestURL):
    if requestURL in jsonByURL:
        return jsonByURL[requestURL]
    for _ in range(5):
        try:
            r = requests.get(url=requestURL, headers=PARAMS)
        except Exception as e:
            print('Exception was caught: ' + repr(e))
            continue

        if r.status_code == 200:
            jsonByURL[requestURL] = r.json()
            return r.json()
        elif r.status_code == 400:
            #malformated URL, e.g. wrong subsystem for bungie
            return None
        else:
            print('request for ' + requestURL + ' failed with code ' + str(r.status_code))
    return None

getSystemByPlayer = {}
def getComponentInfoAsJSON(playerID, components):
    if playerID in getSystemByPlayer:
        url = bungieAPI_URL + '/Destiny2/{}/Profile/{}?components={}'.format(getSystemByPlayer[playerID], playerID, components)
        playerData = getJSONfromURL(url)
        return playerData
    for systemid in [3,2,1,4,5,10,254]: #checking steam, ps, xbox, blizzard, weird ones
        url = bungieAPI_URL + '/Destiny2/{}/Profile/{}?components={}'.format(systemid, playerID, components)
        playerData = getJSONfromURL(url)
        if playerData is not None:
            getSystemByPlayer[playerID] = systemid
            return playerData
    print('getting playerinfo failed')
    return None

def getJSONfromRR(playerID):
    requestURL = 'https://b9bv2wd97h.execute-api.us-west-2.amazonaws.com/prod/api/player/{}'.format(playerID)
    return getJSONfromURL(requestURL)

def getRRLink(bungiePlayerID, system=3):
    url = 'https://www.bungie.net/platform/User/GetMembershipsById/{}/{}/'.format(bungiePlayerID,system)
    r=requests.get(url=url, headers=PARAMS)
    memberships = r.json()['Response']['destinyMemberships']
    for membership in memberships:
        if membership['membershipType'] == 3:
            print('https://raid.report/pc/' + membership['membershipId'])


def playerHasCollectible(playerid, cHash, systemid=3):
    userCollectibles = getComponentInfoAsJSON(playerid, 800)
    collectibles = userCollectibles['Response']['profileCollectibles']['data']['collectibles']
    return collectibles[str(cHash)]['state'] == 0

playerActivities = {} #used as cache for getClearCount per player
def getClearCount(playerid, activityHash):
    if not playerid in playerActivities.keys():
        profileInfo = getJSONfromRR(playerid)
        playerActivities[playerid] = profileInfo['response']['activities'] # list of dicts that contain activityHash and values

    counter = 0
    for activityInfo in playerActivities[playerid]:
        if activityInfo['activityHash'] == activityHash:
            counter += activityInfo['values']['fullClears']
    return counter

def flawlessList(playerid):
    profileInfo = getJSONfromRR(playerid)
    activities = profileInfo['response']['activities']

    flawlessL = []
    for raid in activities:
        if 'flawlessDetails' in raid['values'].keys():
            flawlessL.append(raid['activityHash'])
    return flawlessL

def getTriumphsJSON(playerID, system=3):
    achJSON = getComponentInfoAsJSON(playerID, 900)
    return achJSON['Response']['profileRecords']['data']['records']

def playerHasTriumph(playerid, recordHash):
    status = True
    triumphs = getTriumphsJSON(playerid)
    if recordHash not in triumphs:
        return False
    for part in triumphs[recordHash]['objectives']:
        status &= part['complete']
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

def getPlayerRoles(playerid):		
    roles = []		
    for year, yeardata in requirementHashes.items():		
        for role in yeardata.keys():		
            if playerHasRole(playerid, role, year):		
                roles.append(role)		
    return roles

def getNameToHashMapByClanid(clanid):
    requestURL = bungieAPI_URL + "/GroupV2/{}/members/".format(clanid) #bloodoak memberlist
    memberJSON = getJSONfromURL(requestURL)
    memberlist = memberJSON['Response']['results']
    memberids  = dict()
    for member in memberlist:
        memberids[member['destinyUserInfo']['LastSeenDisplayName']] = member['destinyUserInfo']['membershipId']
    return memberids