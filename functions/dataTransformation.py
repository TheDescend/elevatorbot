import pathlib
from datetime import datetime
import time

import matplotlib

from functions.dataLoading import getStats, getTriumphsJSON, getPGCR, getPlayersPastActivities, getNameToHashMapByClanid
from functions.network import getComponentInfoAsJSON
from static.dict import clanids, seasonalChallengesCategoryHash
from functions.database import getInfoOnLowManActivity, getDestinyDefinition, getSeals, getEverything, getEverythingRow

matplotlib.use('Agg')
import matplotlib.pyplot as plt

#https://data.destinysets.com/

async def hasCollectible(playerid, cHash):
    """ Returns boolean whether the player <playerid> has the collecible <cHash> """
    userCollectibles = await getComponentInfoAsJSON(playerid, 800)
    if not userCollectibles or 'data' not in userCollectibles['Response']['profileCollectibles']:
        return False
    collectibles = userCollectibles['Response']['profileCollectibles']['data']['collectibles']
    if str(cHash) not in collectibles:
        return False
    return collectibles[str(cHash)]['state'] & 1 == 0
#   Check whether it's not (not aquired), which means that the firstbit can't be 1   
#   https://bungie-net.github.io/multi/schema_Destiny-DestinyCollectibleState.html

async def hasTriumph(playerid, recordHash):
    """ returns True if the player <playerid> has the triumph <recordHash> """
    status = True
    triumphs = await getTriumphsJSON(playerid)
    if triumphs is None:
        return False
    if str(recordHash) not in triumphs:
        return False
    #print(triumphs[str(recordHash)])
    if not 'objectives' in triumphs[str(recordHash)]:
        assert triumphs[str(recordHash)]['state'] & 2 #make sure it's RewardUnavailable aka legacy 
        #https://bungie-net.github.io/multi/schema_Destiny-DestinyRecordState.html#schema_Destiny-DestinyRecordState
        status &= (triumphs[str(recordHash)]['state'] & 1)
        return status
    for part in triumphs[str(recordHash)]['objectives']:
        status &= part['complete']
    return status

async def getPlayerCount(instanceID):
    pgcr = await getPGCR(instanceID)
    ingamechars = pgcr['Response']['entries']
    ingameids = set()
    for char in ingamechars:
        ingameids.add(char['player']['destinyUserInfo']['membershipId'])
    return len(ingameids)


async def hasLowman(playerid, playercount, raidHashes, flawless=False, noCheckpoints=False, disallowed=[], score_threshold=False):
    """ Default is flawless=False, disallowed is a list of (starttime, endtime) with datetime objects """
    starttime = time.monotonic()
    low_activity_info = await getInfoOnLowManActivity(
        raidHashes,
        playercount,
        playerid,
        noCheckpoints,
        score_threshold
    )
    print(f"getInfoOnLowManActivity took {(time.monotonic()-starttime)} seconds")

    for (iid, deaths, kills, timePlayedSeconds, period) in low_activity_info:
        # check for flawless if asked for
        if not flawless or deaths == 0:
            verdict = True

            for starttime, endtime in disallowed:
                if starttime < period < endtime:
                    verdict = False
            if 910380154 in raidHashes and kills * 60 / timePlayedSeconds < 1:
                verdict = False
            if verdict:
                return True
    return False

async def getIntStat(destinyID, statname):
    stats = await getStats(destinyID)
    if not stats:
        return -1
    stat = stats['mergedAllCharacters']['merged']['allTime'][statname]['basic']['value']
    return int(stat)

async def getCharStats(destinyID, characterID, statname):
    stats = await getStats(destinyID)
    for char in stats['characters']:
        if char['characterId'] == str(characterID):
            return char['merged']['allTime'][statname]['basic']['value']

async def getPossibleStats():
    stats = await getStats(4611686018468695677)
    for char in stats['characters']:
        return char['merged']['allTime'].keys()

async def isUserInClan(destinyID, clanid):
    isin = destinyID in await getNameToHashMapByClanid(clanid).values()
    print(f'{destinyID} is {isin} in {clanid}')
    return isin

fullMemberMap = {}
async def getFullMemberMap():
    if len(fullMemberMap) > 0:
        return fullMemberMap
    else:
        for clanid in clanids:
            fullMemberMap.update(await getNameToHashMapByClanid(clanid))
        return fullMemberMap

async def getGunsForPeriod(destinyID, pStart, pEnd):
    processes = []

    async for pve in getPlayersPastActivities(destinyID):
        if 'period' not in pve.keys():
            continue
        period = datetime.strptime(pve['period'], "%Y-%m-%dT%H:%M:%SZ")
        pS = datetime.strptime(pStart, "%Y-%m-%d")
        pE = datetime.strptime(pEnd, "%Y-%m-%d")

        if pS < period < pE:
            result = await getPGCR(pve['activityDetails']['instanceId'])
            if result['Response']:
                for entry in result['Response']['entries']:
                    if int(entry['player']['destinyUserInfo']['membershipId']) != int(destinyID):
                        # print(entry['player']['destinyUserInfo'])
                        continue
                    if not 'weapons' in entry['extended'].keys():
                        continue
                    # guns = entry['extended']['weapons']
                    # for gun in guns:
                    #     # gunids.append(gun['referenceId'])
                    #     if str(gun['referenceId']) not in gunkills:
                    #         gunkills[str(gun['referenceId'])] = 0
                    #     gunkills[str(gun['referenceId'])] += int(
                    #         gun['values']['uniqueWeaponKills']['basic']['displayValue'])

                # TODO

        if period < pS:
            break


async def getTop10PveGuns(destinyID):
    gunids = []
    gunkills = {}
    activities = getPlayersPastActivities(destinyID)
    instanceIds = [act['activityDetails']['instanceId'] for act in activities]
    pgcrlist = []

    processes = []
    for instanceId in instanceIds:
        result = await getPGCR(instanceId)
        if result:
            pgcrlist.append(result['Response'])

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

    #manifest = getManifestJson()

    #DestinyInventoryItemDefinitionLink = f"https://www.bungie.net{manifest['jsonWorldComponentContentPaths']['en']['DestinyInventoryItemDefinition']}"
    # DestinyInventoryItemDefinitionLink = "https://www.bungie.net/common/destiny2_content/json/en/DestinyInventoryItemDefinition-39a4e3a0-efbe-4356-beca-d87271a5c699.json"
    
    
    
    gunidlist = list(gunkills.keys())
    for gunid in gunidlist:
        (_, _, gunname, *_) = getDestinyDefinition("DestinyInventoryItemDefinition", gunid)
        gunkills[gunname] = int(gunkills[str(gunid)])
        del gunkills[str(gunid)]

    gunkillsorder = sorted(gunkills, reverse=True, key=lambda x : gunkills[x])    

    piedataraw = [gunkills[rankeditem] for rankeditem in gunkillsorder][:10]
    plt.pie(piedataraw, labels=gunkillsorder[:10])
    plt.savefig(f'{destinyID}.png')
    plt.clf()
    return pathlib.Path(__file__).parent / f'{destinyID}.png'


async def getPlayerSeals(destinyID):
    """ returns all the seals and the seals a player has. returns total_seals: list, [[referenceId, titleName], ...]. removes wip seals like WF LW """

    seals = getSeals()
    completed_seals = []
    for seal in seals:
        if await hasTriumph(destinyID, seal[0]):
            completed_seals.append(seal)

    return seals, completed_seals


async def getSeasonalChallengeInfo():
    """
    Returns dict:
    {
        caption:
            [
                {
                    # contains the triumph info
                    'referenceID': id,
                    'name': name,
                    'description': desc
                },
                {
                    ...
                }
            ],
        caption2:
            [
                ...
            ]
    }
    """

    # get categories
    seasonal_challenges = {}
    r1 = await getEverythingRow("DestinyPresentationNodeDefinition", referenceId=seasonalChallengesCategoryHash)
    # loop through those categories and use the "Weekly" one
    for category_hash1 in r1["childrenpresentationnodehash"]:
        async for r2 in getEverything("DestinyPresentationNodeDefinition", referenceId=category_hash1):
            if r2["name"] == "Weekly":
                # get the info for those hashes = {name: [hash]}
                for category_hash2 in r2["childrenpresentationnodehash"]:
                    r3 = await getEverythingRow("DestinyPresentationNodeDefinition", referenceId=category_hash2)
                    referenceIDs = r3["childrenrecordhash"]
                    seasonal_challenges[r3["name"]] = []

                    # loop through referenceIDs
                    for referenceID in referenceIDs:
                        # getting name / desc
                        r4 = await getEverythingRow("DestinyRecordDefinition", ["name", "description"], referenceId=referenceID)
                        name = r4["name"]
                        description = r4["description"]

                        # adding info to dict
                        seasonal_challenges[r3["name"]].append({
                            "referenceID": referenceID,
                            "name": name,
                            "description": description
                        })

    return seasonal_challenges
