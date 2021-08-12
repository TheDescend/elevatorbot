from datetime import timedelta
import time
from typing import Union, Optional

import matplotlib
import time
from datetime import timedelta
from typing import Union, Optional

import matplotlib

matplotlib.use('Agg')

from functions.dataLoading import getStats, get_triumphs_json, get_pgcr, getNameToHashMapByClanid, getProfile
from static.dict import clanids, seasonalChallengesCategoryHash
from database.database import get_info_on_low_man_activity, getSeals, getEverything, getEverythingRow, \
    insertEmblem, hasEmblem



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
