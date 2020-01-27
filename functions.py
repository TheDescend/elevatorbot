import requests

import config
from dict import platform,requirementHashes, clanids
from fuzzywuzzy import fuzz
import discord
import json
from database import insertUser, lookupUser
import time
import logging
import http.client

if False:
    http.client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    req_log = logging.getLogger('requests.packages.urllib3')
    req_log.setLevel(logging.DEBUG)
    req_log.propagate = True

bungieAPI_URL = "https://www.bungie.net/Platform"
PARAMS = {'X-API-Key': config.BUNGIE_TOKEN}

jsonByURL = {}
session = requests.Session()
def getJSONfromURL(requestURL):
    #print(jsonByURL) #TODO
    if requestURL in jsonByURL:
        return jsonByURL[requestURL]
    for _ in range(3):
        try:
            r = session.get(url=requestURL, headers=PARAMS)
        except Exception as e:
            print('Exception was caught: ' + repr(e))
            continue

        if r.status_code == 200:
            jsonByURL[requestURL] = r.json()
            return r.json()
        elif r.status_code == 400:
            #malformated URL, e.g. wrong subsystem for bungie
            return None
        elif r.status_code == 404:
            print('no stats found')
            return None
        elif r.status_code == 500:
            #print(r.content)
            return None
        else:
            print('failed with code ' + str(r.status_code) + (', because servers are busy' if ('ErrorCode' in r.json() and r.json()['ErrorCode']==1672) else ''))
    print('request failed 3 times') 
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

def getIDfromBungie(bungiePlayerID, system=None):
    if system:
        url = 'https://www.bungie.net/platform/User/GetMembershipsById/{}/{}/'.format(bungiePlayerID,system)
        r=requests.get(url=url, headers=PARAMS)
        memberships = r.json()['Response']['destinyMemberships']
        for membership in memberships:
            if membership['membershipType'] == 3:
                return membership['membershipId']
    else:
        for systemid in [3,2,1,4,5,10,254]:
            url = 'https://www.bungie.net/platform/User/GetMembershipsById/{}/{}/'.format(bungiePlayerID,systemid)
            resp = getJSONfromURL(url)
            if not resp:
                continue
            memberships = resp['Response']['destinyMemberships']
            for membership in memberships:
                if membership['membershipType'] == 3:
                    return membership['membershipId']
def getRRLink(bungiePlayerID, system=3):
    print('https://raid.report/pc/' +getIDfromBungie(bungiePlayerID, system))


def playerHasCollectible(playerid, cHash, systemid=3):
    userCollectibles = getComponentInfoAsJSON(playerid, 800)
    if not userCollectibles or 'data' not in userCollectibles['Response']['profileCollectibles']:
        return False
    collectibles = userCollectibles['Response']['profileCollectibles']['data']['collectibles']
    return collectibles[str(cHash)]['state'] == 0

# def printInventoryItem(chash=1057119308, playerid=4611686018451177627):#spire star
#     userCollectibles = getComponentInfoAsJSON(playerid, 800)
#     if not userCollectibles or 'data' not in userCollectibles['Response']['profileCollectibles']:
#         return False
#     collectibles = userCollectibles['Response']['profileCollectibles']['data']['collectibles']
#     return collectibles[str(chash)]
#print(printCollectible())


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
        #print(playerActivities)
    counter = 0
    for activityInfo in playerActivities[playerid]:
        if activityInfo['activityHash'] == activityHash:
            counter += activityInfo['values']['fullClears']
    return counter

#print(getClearCount(4611686018451177627, 119944200))
    

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

playerpastraidscache = {}
def getPlayersPastRaids(destinyID):
    if str(destinyID) in playerpastraidscache.keys():
        return playerpastraidscache[str(destinyID)]
    charURL = "https://stats.bungie.net/Platform/Destiny2/{}/Profile/{}/?components=100,200"
    characterinfo = None
    platform = None
    for system in [3,2,1,4,5,10,254]:
        characterinfo = getJSONfromURL(charURL.format(system, destinyID))
        if characterinfo:
            platform = system
            break
    charIDs = characterinfo['Response']['characters']['data'].keys()
    activitylist = []
    for characterID in charIDs:
        for pagenr in range(100):
            staturl = f"https://www.bungie.net/Platform/Destiny2/{platform}/Account/{destinyID}/Character/{characterID}/Stats/Activities/?mode=4&count=250&page={pagenr}" #mode=4 for raids
            rep = getJSONfromURL(staturl)
            if not rep:
                break
            activitylist.append(rep['Response'])
    playerpastraidscache[str(destinyID)] = activitylist
    return activitylist

def playerHasRole(playerid, role, year):
    roledata = requirementHashes[year][role]
    if not 'requirements' in roledata:
        print('malformatted requirementHashes')
        return False
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
        elif req == 'lowman':
            for activitylist in getPlayersPastRaids(playerid):
                if 'activities' not in activitylist.keys():
                    continue
                for activity in activitylist['activities']:
                    hasCompleted = activity['values']['completed']['basic']['value'] == 1
                    playercount = activity['values']['playerCount']['basic']['value']
                    activityhash = activity['activityDetails']['directorActivityHash']
                    #print(hasCompleted, ' and ', playercount == roledata['playercount'], ' and ', activityhash, activityhash in roledata['activityHashes'])
                    if hasCompleted and playercount == roledata['playercount'] and activityhash in roledata['activityHashes']:
                        return True
            return False
        elif req == 'roles':
            return False
    return True

#print(playerHasRole(4611686018467544385, 'Two-Man Argos', 'Addition'))




#returns (roles, redundantroles)
def getPlayerRoles(playerid):
    print(f'getting roles for {playerid}')
    roles = []
    redundantRoles = []
    forbidden = []
    for year, yeardata in requirementHashes.items():		
        for role, roledata in yeardata.items():
            if playerHasRole(playerid, role, year) and role not in forbidden:
                roles.append(role)

    for yeardata in requirementHashes.values():
        for role, roledata in yeardata.items():
            if 'replaced_by' in roledata.keys():
                for superior in roledata['replaced_by']:
                    if superior in roles and role in roles:
                        roles.remove(role)
                        redundantRoles.append(role)
    
    for yeardata in requirementHashes.values():
        for role, roledata in yeardata.items():
            if 'Raid Master' in role:
                worthy = True
                reqs = roledata['roles']
                for reqrole in reqs:
                    if reqrole not in roles:
                        worthy = False
                if worthy:
                    print('worthy for ', role)
                    roles.append(role)
                    for reqrole in reqs:
                        roles.remove(reqrole)
                        redundantRoles.append(reqrole)


    #print(f'getting Roles took {time.time()-starttime}s')
    return (roles, redundantRoles)

def getNameToHashMapByClanid(clanid):
    requestURL = bungieAPI_URL + "/GroupV2/{}/members/".format(clanid) #memberlist
    memberJSON = getJSONfromURL(requestURL)
    if not memberJSON:
        return {}
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
        if maxProb > 70:
            insertUser(discordUser.id, userid, -1)
            print(f'Inserted {discordUser.nick or discordUser.name} because match with {userid} was >70%')
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
    
async def removeRolesFromUser(roleStringList, discordUser, guild):
    removeRolesObjs = []
    for role in roleStringList:
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
    print(f'{destinyID} is {isin} in {clanid}')
    return isin

def addUserMap(discordID, destinyID, serverID):
    if not insertUser(discordID, destinyID, serverID):
        print(f'User with id {discordID} already exists')

#returns destinyID or None
def getUserMap(discordID):
    return lookupUser(discordID)

# def getMultipleUserMap(discordIDlist):
#     returnlist = []
#     with open('userlist', mode='r+') as json_file:
#         data = json.load(json_file)
#         for user in data:
#             [[_discordID, _destinyID]] = user.items()
#             if int(_discordID) in discordIDlist:
#                 returnlist.append((int(_discordID), int(_destinyID)))
#     return returnlist 
