import pathlib
from datetime import datetime, timedelta
import time
from typing import Union, Optional

import matplotlib

from functions.dataLoading import getStats, get_triumphs_json, get_pgcr, getPlayersPastActivities, \
    getNameToHashMapByClanid, getProfile
from static.dict import clanids, seasonalChallengesCategoryHash
from database.database import get_info_on_low_man_activity, getDestinyDefinition, getSeals, getEverything, getEverythingRow

matplotlib.use('Agg')
import matplotlib.pyplot as plt

#https://data.destinysets.com/

# todo ported
async def has_collectible(destiny_id: int, collectible_hash: int) -> bool:
    """ Returns boolean whether the player <playerid> has the collecible <cHash> """

    userCollectibles = await getProfile(destiny_id, 800)
    if not userCollectibles or 'data' not in userCollectibles['profileCollectibles']:
        return False
    collectibles = userCollectibles['profileCollectibles']['data']['collectibles']
    if str(collectible_hash) in collectibles:
        return collectibles[str(collectible_hash)]['state'] & 1 == 0

    # test if its a character specific one
    for character in userCollectibles['characterCollectibles']['data'].values():
        if str(collectible_hash) in character['collectibles']:
            return character['collectibles'][str(collectible_hash)]['state'] & 1 == 0

    return False

#   Check whether it's not (not aquired), which means that the firstbit can't be 1   
#   https://bungie-net.github.io/multi/schema_Destiny-DestinyCollectibleState.html

# todo ported
async def hasTriumph(playerid, recordHash):
    """ returns True if the player <playerid> has the triumph <recordHash> """
    status = True
    triumphs = await get_triumphs_json(playerid)
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

# todo ported
async def getMetricValue(destinyID: int, metric_hash: Union[int, str]):
    """ Returns the value of the given metric hash """

    metrics = (await getProfile(destinyID, 1100))["metrics"]["data"]['metrics']

    if str(metric_hash) in metrics.keys():
        return metrics[str(metric_hash)]["objectiveProgress"]["progress"]
    else:
        return None

# todo ported
async def hasLowman(playerid, playercount, raidHashes, flawless=False, noCheckpoints=False, disallowed=[], score_threshold=False):
    """ Default is flawless=False, disallowed is a list of (starttime, endtime) with datetime objects """
    starttime = time.monotonic()
    low_activity_info = await get_info_on_low_man_activity(
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

# todo ported
async def getIntStat(destinyID, statname, category=None):
    stats = await getStats(destinyID)
    if not stats:
        return -1
    if not category:
        stat = stats['mergedAllCharacters']['merged']['allTime'][statname]['basic']['value']
    else:
        if category == "pve":
            stat = stats['mergedAllCharacters']['results']['allPvE']['allTime'][statname]['basic']['value']
        elif category == "pvp":
            stat = stats['mergedAllCharacters']['results']['allPvP']['allTime'][statname]['basic']['value']
        else:
            return -1

    return int(stat)

# todo ported
async def getCharStats(destinyID, characterID, statname):
    stats = await getStats(destinyID)
    for char in stats['characters']:
        if char['characterId'] == str(characterID):
            return char['merged']['allTime'][statname]['basic']['value']

# todo ported
async def getPlayerSeals(destinyID):
    """ returns all the seals and the seals a player has. returns total_seals: list, [[referenceId, titleName], ...]. removes wip seals like WF LW """

    seals = await getSeals()
    completed_seals = []
    for seal in seals:
        if await hasTriumph(destinyID, seal[0]):
            completed_seals.append(seal)

    return seals, completed_seals

# todo ported
async def get_lowman_count(destiny_id: int, activity_hashes: list[int]) -> list[int, int, Optional[timedelta]]:
    """ Returns [solo_count, solo_is_flawless_count, Optional[solo_fastest]] """
    solo_count, solo_is_flawless_count, solo_fastest = 0, 0, None

    # get player data
    records = await get_info_on_low_man_activity(
        activity_hashes=activity_hashes,
        player_count=1,
        destiny_id=destiny_id,
        no_checkpoints=True
    )

    # prepare player data
    for solo in records:
        solo_count += 1
        if solo["deaths"] == 0:
            solo_is_flawless_count += 1
        if not solo_fastest or (solo["timeplayedseconds"] < solo_fastest):
            solo_fastest = solo["timeplayedseconds"]

    return [solo_count, solo_is_flawless_count, timedelta(seconds=solo_fastest) if solo_fastest else solo_fastest]


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

fullMemberMap = {}
async def getFullMemberMap():
    if len(fullMemberMap) > 0:
        return fullMemberMap
    else:
        for clanid in clanids:
            fullMemberMap.update(await getNameToHashMapByClanid(clanid))
        return fullMemberMap

async def getPlayerCount(instanceID):
    pgcr = await get_pgcr(instanceID)
    ingamechars = pgcr.content['Response']['entries']
    ingameids = set()
    for char in ingamechars:
        ingameids.add(char['player']['destinyUserInfo']['membershipId'])
    return len(ingameids)
