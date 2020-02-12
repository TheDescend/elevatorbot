import requests

import config
from dict import platform,requirementHashes, clanids
from fuzzywuzzy import fuzz
import discord
import json
from database import insertUser, lookupDestinyID
import time
import logging
import http.client
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pathlib

if False:
    http.client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    req_log = logging.getLogger('requests.packages.urllib3')
    req_log.setLevel(logging.DEBUG)
    req_log.propagate = True

bungieAPI_URL = "https://www.bungie.net/Platform"
PARAMS = {'X-API-Key': config.BUNGIE_TOKEN}
dummy = None
session = requests.Session()
def getJSONfromURL(requestURL):
    #print(jsonByURL) #TODO
    for _ in range(3):
        try:
            r = session.get(url=requestURL, headers=PARAMS)
        except Exception as e:
            print('Exception was caught: ' + repr(e))
            continue
        if r.status_code == 200:
            returnval = r.json()
            dummy = r.content[:1]
            return returnval
        elif r.status_code == 400:
            #malformated URL, e.g. wrong subsystem for bungie
            return None
        elif r.status_code == 404:
            print('no stats found')
            dummy = 5
            return None
        elif r.status_code == 500:
            print(f'bad request for {requestURL}')
        elif r.status_code == 503:
            print(f'bungo is ded {dummy}')
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
    return collectibles[str(cHash)]['state'] & 1 == 0

#   None = 0,
#   NotAcquired = 1,
#   Obscured = 2,
#   Invisible = 4,
#   CannotAffordMaterialRequirements = 8,
#   InventorySpaceUnavailable = 16,
#   UniquenessViolation = 32,
#   PurchaseDisabled = 64




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
    if not achJSON:
        return None
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

tempcachepvestats = []
def getPlayersPastPVE(destinyID):
    global tempcachepvestats
    # if len(tempcachepvestats) > 0:
    #     return tempcachepvestats
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
        for pagenr in range(10):
            staturl = f"https://www.bungie.net/Platform/Destiny2/{platform}/Account/{destinyID}/Character/{characterID}/Stats/Activities/?mode=7&count=250&page={pagenr}" #mode=4 for raids, 7 for all  PvE
            rep = getJSONfromURL(staturl)
            if not rep or not rep['Response']:
                break
            activitylist += rep['Response']['activities']
    tempcachepvestats = [a for a in activitylist]
    len(activitylist)
    return activitylist

def getPlayerCount(instanceID):
    pgcr = getPGCR(instanceID)
    ingamechars = pgcr['Response']['entries']
    ingameids = set()
    for char in ingamechars:
        ingameids.add(char['player']['destinyUserInfo']['membershipId'])
    return len(ingameids)

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
            if 'lowman' in roledata['requirements']:
                return True
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
            for activity in getPlayersPastPVE(playerid):
                hasCompleted = activity['values']['completed']['basic']['value'] == 1
                activityhash = activity['activityDetails']['directorActivityHash']
                hasSucceeded = int(activity['values']['completionReason']['basic']['value']) != 2
                #print(hasCompleted, ' and ', playercount == roledata['playercount'], ' and ', activityhash, activityhash in roledata['activityHashes'])
                if hasCompleted and hasSucceeded and activityhash in roledata['activityHashes'] and activity['values']['playerCount']['basic']['value'] < 6:
                    if not 'flawless' in roledata['requirements'] or int(activity['values']['deaths']['basic']['displayValue']) == 0:
                        playercount = getPlayerCount(activity['activityDetails']['instanceId'])
                        #print('role: ' + str(playercount))
                        if playercount == roledata['playercount']:
                            return True
            return False
        elif req == 'roles':
            return False
    return True

#print(playerHasRole(4611686018467544385, 'Two-Man Argos', 'Addition'))
def returnIfHasRoles(playerid, role, year):
    if playerHasRole(playerid, role, year):
        return role
    return None

def getPlayerRoles(playerid, existingRoles = []):
    print(f'getting roles for {playerid}')
    roles = []
    redundantRoles = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        processes = []
        for year, yeardata in requirementHashes.items():		
            for role, roledata in yeardata.items():
                # if role in existingRoles or ('replaced_by' in roledata.keys() and any([x in existingRoles for x in roledata['replaced_by']])):
                #     roles.append(role)
                #     continue
                processes.append(executor.submit(returnIfHasRoles, playerid, role, year))

    for task in as_completed(processes):
        if task.result():
            roles.append(task.result())

    for yeardata in requirementHashes.values():
        for role, roledata in yeardata.items():
            if role not in roles:
                redundantRoles.append(role)
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
                    redundantRoles.remove(role)
                    for reqrole in reqs:
                        roles.remove(reqrole)
                        redundantRoles.append(reqrole)

    global tempcachepvestats
    tempcachepvestats = []
    #print(f'getting Roles took {time.time()-starttime}s')
    return (roles, redundantRoles)

def getPlayerStats(destinyID):
    url = 'https://stats.bungie.net/Platform/Destiny2/{}/Account/{}/Stats/?groups=weapons'
    for system in [3,2,1,4,5,10,254]:
        statsResponse = getJSONfromURL(url.format(system, destinyID))
        if statsResponse:
            return statsResponse['Response']
    return None

def getIntStat(destinyID, statname):
    stats = getPlayerStats(destinyID)
    stat =  stats['mergedAllCharacters']['merged']['allTime'][statname]['basic']['value']
    return int(stat)

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
            insertUser(-1, discordID = discordUser.id, destinyID = userid)
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

def getCharacterList(destinyID):
    charURL = "https://stats.bungie.net/Platform/Destiny2/{}/Profile/{}/?components=100,200"
    platform = None
    for i in [3,2,1,4,5,10,254]:
        characterinfo = getJSONfromURL(charURL.format(i, destinyID))
        if characterinfo:
            break
    return characterinfo['Response']['characters']['data'].keys()

def getPlatform(destinyID):
    charURL = "https://stats.bungie.net/Platform/Destiny2/{}/Profile/{}/?components=100,200"
    platform = None
    for i in [3,2,1,4,5,10,254]:
        characterinfo = getJSONfromURL(charURL.format(i, destinyID))
        if characterinfo:
            break
    return platform

fullMemberMap = {}
def getFullMemberMap():
    if len(fullMemberMap) > 0:
        return fullMemberMap
    else:
        for clanid in clanids:
            fullMemberMap.update(getNameToHashMapByClanid(clanid))
        return fullMemberMap

def isUserInClan(destinyID, clanid):
    isin = destinyID in getNameToHashMapByClanid(clanid).values()
    print(f'{destinyID} is {isin} in {clanid}')
    return isin

def addUserMap(discordID, destinyID, serverID):
    if not insertUser(discordID, destinyID, serverID):
        print(f'User with id {discordID} already exists')

#returns destinyID or None
def getUserMap(discordID):
    return lookupDestinyID(discordID)

# def getMultipleUserMap(discordIDlist):
#     returnlist = []
#     with open('userlist', mode='r+') as json_file:
#         data = json.load(json_file)
#         for user in data:
#             [[_discordID, _destinyID]] = user.items()
#             if int(_discordID) in discordIDlist:
#                 returnlist.append((int(_discordID), int(_destinyID)))
#     return returnlist 

manifest = {}
def getManifestJson():
    global manifest
    if manifest:
        return manifest
    manifesturl = 'https://www.bungie.net/Platform/Destiny2/Manifest/'
    manifestresponse = getJSONfromURL(manifesturl)
    manifest = manifestresponse['Response']
    return manifest

def getPGCR(instanceID):
    pgcrurl = f'https://www.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{instanceID}/'
    return getJSONfromURL(pgcrurl)

def getTop10PveGuns(destinyID):
    gunids = []
    gunkills = {}
    activities = getPlayersPastPVE(destinyID)
    instanceIds = [act['activityDetails']['instanceId'] for act in activities]
    pgcrlist = []

    processes = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        for instanceId in instanceIds:
            processes.append(executor.submit(getPGCR, instanceId))

    for task in as_completed(processes):
        if task.result():
            pgcrlist.append(task.result()['Response'])

    for pgcr in pgcrlist:
        for entry in pgcr['entries']:
            if int(entry['player']['destinyUserInfo']['membershipId']) != int(destinyID):
               # print(entry['player']['destinyUserInfo'])
                continue
            if not 'weapons' in entry['extended'].keys():
                continue
            guns = entry['extended']['weapons']
            for gun in guns:
                #gunids.append(gun['referenceId'])
                if str(gun['referenceId']) not in gunkills:
                    gunkills[str(gun['referenceId'])] = 0
                gunkills[str(gun['referenceId'])] += int(gun['values']['uniqueWeaponKills']['basic']['displayValue'])

    manifest = getManifestJson()

    DestinyInventoryItemDefinitionLink = f"https://www.bungie.net{manifest['jsonWorldComponentContentPaths']['en']['DestinyInventoryItemDefinition']}"
    inventoryitemdefinition = getJSONfromURL(DestinyInventoryItemDefinitionLink)
    gunidlist = list(gunkills.keys())
    for gunid in gunidlist:
        gunname = inventoryitemdefinition[str(gunid)]['displayProperties']['name']
        gunkills[gunname] = int(gunkills[str(gunid)])
        del gunkills[str(gunid)]

    gunkillsorder = sorted(gunkills, reverse=True, key=lambda x : gunkills[x])    

    piedataraw = [gunkills[rankeditem] for rankeditem in gunkillsorder][:10]
    plt.pie(piedataraw, labels=gunkillsorder[:10])
    plt.savefig(f'{destinyID}.png')
    plt.clf()
    return pathlib.Path(__file__).parent / f'{destinyID}.png'