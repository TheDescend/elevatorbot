import requests

import config
from dict import platform,requirementHashes, clanids
from fuzzywuzzy import fuzz
import discord

bungieAPI_URL = "https://www.bungie.net/Platform"
PARAMS = {'X-API-Key': config.BUNGIE_TOKEN}

jsonByURL = {}
def getJSONfromURL(requestURL):
    if requestURL in jsonByURL:
        return jsonByURL[requestURL]
    for _ in range(3):
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
            #print('request for ' + requestURL + ' failed with code ' + str(r.status_code))
            pass
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

def getIDfromBungie(bungiePlayerID, system):
    url = 'https://www.bungie.net/platform/User/GetMembershipsById/{}/{}/'.format(bungiePlayerID,system)
    r=requests.get(url=url, headers=PARAMS)
    memberships = r.json()['Response']['destinyMemberships']
    for membership in memberships:
        if membership['membershipType'] == 3:
            return membership['membershipId']

def getRRLink(bungiePlayerID, system=3):
    print('https://raid.report/pc/' +getIDfromBungie(bungiePlayerID, system))


def playerHasCollectible(playerid, cHash, systemid=3):
    userCollectibles = getComponentInfoAsJSON(playerid, 800)
    if 'data' not in userCollectibles['Response']['profileCollectibles']:
        return False
    collectibles = userCollectibles['Response']['profileCollectibles']['data']['collectibles']
    return collectibles[str(cHash)]['state'] == 0

playerActivities = {} #used as cache for getClearCount per player
nodata = []
def getClearCount(playerid, activityHash):
    if playerid in nodata:
        return 0
    if not playerid in playerActivities.keys():
        profileInfo = getJSONfromRR(playerid)
        if profileInfo is None:
            nodata.append(playerid)
            return -1
        playerActivities[playerid] = profileInfo['response']['activities'] # list of dicts that contain activityHash and values

    counter = 0
    for activityInfo in playerActivities[playerid]:
        if activityInfo['activityHash'] == activityHash:
            counter += activityInfo['values']['fullClears']
    return counter

def flawlessList(playerid):
    profileInfo = getJSONfromRR(playerid)
    if profileInfo is None:
        return []
    activities = profileInfo['response']['activities']

    flawlessL = []
    for raid in activities:
        if 'flawlessDetails' in raid['values'].keys():
            flawlessL.append(raid['activityHash'])
    return flawlessL

def getTriumphsJSON(playerID, system=3):
    achJSON = getComponentInfoAsJSON(playerID, 900)
    if 'data' not in achJSON['Response']['profileRecords']:
        return None
    return achJSON['Response']['profileRecords']['data']['records']

def playerHasTriumph(playerid, recordHash):
    status = True
    triumphs = getTriumphsJSON(playerid)
    if triumphs is None:
        return False
    if str(recordHash) not in triumphs:
        return False
    for part in triumphs[str(recordHash)]['objectives']:
        status &= part['complete']
    return status

def playerHasClears(playerid, n, raidHashes):
    count = 0
    for h in raidHashes:
        count += getClearCount(playerid, h)
    #print(str(count >= n) + ' for ' + str(raidHashes))
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
                    #print('failed clears for ' + str(raid['actHashes']))
                    return False
        elif req == 'flawless':
            if not playerHasFlawless(playerid, roledata['flawless']):
                #print('failed flawless for ' + str(roledata['flawless']))
                return False
        elif req == 'collectibles':
            for collectible in roledata['collectibles']:
                if not playerHasCollectible(playerid, collectible):
                    #print('failed collectible: '+ str(collectible))
                    return False
        elif req == 'records':
            for recordHash in roledata['records']:
                if not playerHasTriumph(playerid, recordHash):
                    #print('failed triumph: ' + str(recordHash))
                    return False
    return True

def getPlayerRoles(playerid):		
    print(f'getting roles for {playerid}')
    roles = []
    redundantRoles = []
    forbidden = []
    for year, yeardata in requirementHashes.items():		
        for role, roledata in yeardata.items():		
            if playerHasRole(playerid, role, year) and role not in forbidden:
                roles.append(role)
            else:
                if 'replaced_by' in roledata:
                    forbidden.append(roledata['replaced_by'])
    if True:
        for yeardata in requirementHashes.values():
            for role, roledata in yeardata.items():
                if 'replaced_by' in roledata.keys():
                    if roledata['replaced_by'] in roles and role in roles:
                        roles.remove(role)
                        redundantRoles.append(role)
    return (roles, redundantRoles)

def getNameToHashMapByClanid(clanid):
    requestURL = bungieAPI_URL + "/GroupV2/{}/members/".format(clanid) #memberlist
    memberJSON = getJSONfromURL(requestURL)
    memberlist = memberJSON['Response']['results']
    memberids  = dict()
    for member in memberlist:
        memberids[member['destinyUserInfo']['LastSeenDisplayName']] = member['destinyUserInfo']['membershipId']
    return memberids


def getUserIDbySnowflakeAndClanLookup(discordUser, memberMap):
        username = discordUser.nick or discordUser.name
        maxName = None
        maxProb = 50
        for ingameName in memberMap.keys():
            uqprob = fuzz.UQRatio(username, ingameName)
            if uqprob > maxProb:
                maxProb = uqprob
                maxName = ingameName
        if not maxName:
            return None
        steamName = maxName
        userid = memberMap[steamName]
        return userid

async def assignRolesToUser(roleList, discordUser, guild):
    #takes rolelist as string array, userSnowflake, guild object
    for role in roleList:
        roleObj = discord.utils.get(guild.roles, name=role)
        if roleObj is None:
            print(f'role doesn\'t exist: {role}')
            continue
        if roleObj not in discordUser.roles:
            print(f'added role {roleObj.name} to user {discordUser.name}')
            await discordUser.add_roles(roleObj)
    
async def removeRolesFromUser(roleList, discordUser, guild):
    removeRolesObjs = []
    for role in roleList:
        roleObj = discord.utils.get(guild.roles, name=role)
        if roleObj is None:
            print(f'role doesn\'t exist: {role}')
            continue
        removeRolesObjs.append(roleObj)
    for roleObj in removeRolesObjs:
        #print(f'removed {roleObj.name} from {discordUser.name}')
        if roleObj in discordUser.roles:
            print(f'removed role {roleObj.name} from user {discordUser.name}')
            await discordUser.remove_roles(roleObj, reason='better role present')

fullMemberMap = {}
def getFullMemberMap():
    if len(fullMemberMap) > 0:
        return fullMemberMap
    else:
        for clanid in clanids:
            fullMemberMap.update(getNameToHashMapByClanid(clanid))

def isUserInClan(destinyID, clanid):
    isin = destinyID in getNameToHashMapByClanid(clanid).values()
    #print(f'{destinyID} is {isin} in {clanid}')
    return isin