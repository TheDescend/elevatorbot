import asyncio
import logging
from datetime import datetime

from functions.database import get_connection_pool, updateLastUpdated, \
    lookupDiscordID, lookupSystem, insertPgcrActivities, getPgcrActivity, insertPgcrActivitiesUsersStats, \
    insertPgcrActivitiesUsersStatsWeapons, getFailToGetPgcrInstanceId, insertFailToGetPgcrInstanceId, \
    deleteFailToGetPgcrInstanceId, getWeaponInfo, updateDestinyDefinition, getVersion, updateVersion, deleteEntries
from functions.database import getLastUpdated
from functions.formating import embed_message
from functions.network import getJSONfromURL, getComponentInfoAsJSON, getJSONwithToken
from static.config import CLANID



async def getJSONfromRR(playerID):
    """ Gets a Players stats from the RR-API """
    requestURL = 'https://b9bv2wd97h.execute-api.us-west-2.amazonaws.com/prod/api/player/{}'.format(playerID)
    return await getJSONfromURL(requestURL)

async def getTriumphsJSON(playerID):
    """ returns the json containing all triumphs the player <playerID> has """
    achJSON = await getComponentInfoAsJSON(playerID, 900)
    if not achJSON:
        return None
    if 'data' not in achJSON['Response']['profileRecords']:
        return None
    profileRecs = achJSON['Response']['profileRecords']['data']['records']
    charRecs = [charrecords['records'] for charid, charrecords in achJSON['Response']['characterRecords']['data'].items()]
    for chardic in charRecs:
        profileRecs.update(chardic)
    return profileRecs #reduce(lambda d1,d2: d1|d2, charRecs, initializer=profileRecs)

async def getCharacterList(destinyID):
    ''' returns a (system, [characterids]) tuple '''
    charURL = "https://stats.bungie.net/Platform/Destiny2/{}/Profile/{}/?components=100,200"
    membershipType = lookupSystem(destinyID)
    characterinfo = await getJSONfromURL(charURL.format(membershipType, destinyID))
    if characterinfo:
        return (membershipType, list(characterinfo['Response']['characters']['data'].keys()))
    print(f'no account found for destinyID {destinyID}')
    return (None,[])

# todo get from DB
racemap = {
    2803282938: 'Awoken',
    898834093: 'Exo',
    3887404748: 'Human'
} 
gendermap = {
    2204441813: 'Female',
    3111576190: 'Male',
}
classmap = {
    671679327: 'Hunter',
    2271682572: 'Warlock',
    3655393761: 'Titan'
}


async def getCharacterInfoList(destinyID):
    """
    returns more detailed character info.
    return = (
        [characterID1, ...],
        {
            characterID1: {
                "class": str,
                "race": str,
                "gender": str
            },
            ...
        }
    )
    """
    membershipType = lookupSystem(destinyID)

    # get char data
    charURL = f"https://stats.bungie.net/Platform/Destiny2/{membershipType}/Profile/{destinyID}/?components=200"
    res = await getJSONfromURL(charURL)
    char_list = []
    char_data = {}
    if res:
        # loop through each character
        for characterID, character_data in res['Response']['characters']['data'].items():
            characterID = int(characterID)

            # format the data correctly and convert the hashes to strings
            char_list.append(characterID)
            char_data[characterID] = {
                "class": classmap[character_data["classHash"]],
                "race": racemap[character_data["raceHash"]],
                "gender": gendermap[character_data["genderHash"]]
            }

        return char_list, char_data

    # if that fails for some reason
    print(f'No account found for destinyID {destinyID}')
    return None, None


async def getCharactertypeList(destinyID):
    ''' returns a [charID, type] tuple '''
    charURL = "https://stats.bungie.net/Platform/Destiny2/{}/Profile/{}/?components=100,200"
    membershipType = lookupSystem(destinyID)
    characterinfo = await getJSONfromURL(charURL.format(membershipType, destinyID))
    if characterinfo:
        return [(char["characterId"], f"{racemap[char['raceHash']]} {gendermap[char['genderHash']]} {classmap[char['classHash']]}") for char in characterinfo['Response']['characters']['data'].values()]
    print(f'no account found for destinyID {destinyID}')
    return (None,[])


async def getCharacterID(destinyID, classID):
    ''' returns a charID '''
    charIDs = (await getCharactertypeList(destinyID))[0]
    membershipType = lookupSystem(destinyID)

    charURL = "https://stats.bungie.net/Platform/Destiny2/{}/Profile/{}/Character/{}/?components=100,200"
    for charID in charIDs:
        characterinfo = await getJSONfromURL(charURL.format(membershipType, destinyID, charID))
        if characterinfo:
            if classID == characterinfo['Response']['character']['data']['classHash']:
                return charID

    return None


async def getPlayersPastActivities(destinyID, mode : int = 7, earliest_allowed_time : datetime = None, latest_allowed_time : datetime = None):
    """
    Generator which returns all activities whith an extra field < activity['charid'] = characterID >
    For more Info visit https://bungie-net.github.io/multi/schema_Destiny-HistoricalStats-DestinyHistoricalStatsPeriodGroup.html#schema_Destiny-HistoricalStats-DestinyHistoricalStatsPeriodGroup

    :mode - Describes the mode, see https://bungie-net.github.io/multi/schema_Destiny-HistoricalStats-Definitions-DestinyActivityModeType.html#schema_Destiny-HistoricalStats-Definitions-DestinyActivityModeType
        Everything	0
        Story	    2
        Strike	    3
        Raid	    4
        AllPvP	    5
        Patrol	    6
        AllPvE	    7
        ...
    :earliest_allowed_time - takes datetime.datetime and describes the lower cutoff
    :latest_allowed_time - takes datetime.datetime and describes the higher cutoff
    """

    platform, charIDs = await getCharacterList(destinyID)

    # if player has no characters for some reason
    if not charIDs:
        return

    for characterID in charIDs:
        br = False
        page = -1
        while True:
            page += 1
            staturl = f"https://www.bungie.net/Platform/Destiny2/{platform}/Account/{destinyID}/Character/{characterID}/Stats/Activities/?mode={mode}&count=250&page={page}"

            # break once threshold is reached
            if br:
                break

            # get activities
            rep = await getJSONfromURL(staturl)

            # break if empty, fe. when pages are over
            if not rep or not rep['Response']:
                break

            # loop through all activities
            for activity in rep['Response']['activities']:
                # check times if wanted
                if earliest_allowed_time or latest_allowed_time:
                    activity_time = datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ")

                    # check if the activity started later than the earliest allowed, else break and continue with next char
                    # This works bc Bungie sorts the api with the newest entry on top
                    if earliest_allowed_time:
                        if activity_time <= earliest_allowed_time:
                            br = True
                            break

                    # check if the time is still in the timeframe, else pass this one and do the next
                    if latest_allowed_time:
                        if activity_time > latest_allowed_time:
                            pass

                # add character info to the activity
                activity['charid'] = characterID

                yield activity


# https://bungie-net.github.io/multi/schema_Destiny-DestinyComponentType.html#schema_Destiny-DestinyComponentType
async def getProfile(destinyID, *components, with_token=False):
    url = 'https://stats.bungie.net/Platform/Destiny2/{}/Profile/{}/?components={}'
    membershipType = lookupSystem(destinyID)
    if with_token:
        statsResponse = await getJSONwithToken(url.format(membershipType, destinyID, ','.join(map(str, components))), lookupDiscordID(destinyID))
        if statsResponse["result"]:
            return statsResponse["result"]['Response']

    else:
        statsResponse = await getJSONfromURL(url.format(membershipType, destinyID, ','.join(map(str, components))))
        if statsResponse:
            return statsResponse['Response']
    return None


async def getStats(destinyID):
    url = 'https://stats.bungie.net/Platform/Destiny2/{}/Account/{}/Stats/'
    membershipType = lookupSystem(destinyID)
    statsResponse = await getJSONfromURL(url.format(membershipType, destinyID))
    if statsResponse:
        return statsResponse['Response']
    return None


async def getAggregateStatsForChar(destinyID, system, characterID):
    url = 'https://stats.bungie.net/Platform/Destiny2/{}/Account/{}/Character/{}/Stats/AggregateActivityStats/'
    statsResponse = await getJSONfromURL(url.format(system, destinyID, characterID))
    if statsResponse:
        return statsResponse['Response']
    return None


# returns the item data - https://bungie-net.github.io/#/components/schemas/Destiny.Entities.Items.DestinyItemComponent
async def getItemDefinition(destinyID, system, itemID, components):
    url = 'https://stats.bungie.net/Platform/Destiny2/{}/Profile/{}/Item/{}/?components={}'
    statsResponse = await getJSONfromURL(url.format(system, destinyID, itemID, components))
    if statsResponse:
        return statsResponse['Response']
    return None


# gets the weapon (name, [hash1, hash2, ...]) for the search term for all weapons found
# more than one weapon can be found if it got reissued
async def searchForItem(client, message, search_term):
    # search for the weapon in the api
    info = await getJSONfromURL(f'http://www.bungie.net/Platform/Destiny2/Armory/Search/DestinyInventoryItemDefinition/{search_term}/')
    data = {}
    try:
        for weapon in info["Response"]["results"]["results"]:
            # only add weapon if its not a catalyst
            if "catalyst" not in weapon["displayProperties"]["name"].lower():
                n = weapon["displayProperties"]["name"]
                h = weapon["hash"]

                if n not in data:
                    data[n] = [h]
                else:
                    data[n].append(h)

        if not data:
            raise KeyError

    # if no weapon was found
    except KeyError:
        await message.reply(embed=embed_message(
            "Error",
            f'I do not know the weapon "{search_term}"'
        ))
        return None, None

    # check if we found multiple items with different names. Ask user to specify which one is correct
    index = 0
    if len(data) > 1:
        # asking user for the correct item
        text = "Multiple items can be found with that search term, please specify which item you meant by sending the corresponding number:\n\u200B"
        i = 1
        for name in data.keys():
            text += f"\n**{i}** - {name}"
            i += 1
        msg = await message.reply(embed=embed_message(
            f'{message.author.display_name}, I need one more thing',
            text
        ))

        # to check whether or not the one that send the msg is the original author for the function after this
        def check(answer_msg):
            return answer_msg.author == message.author and answer_msg.channel == message.channel

        # wait for reply from original user to set the time parameters
        try:
            answer_msg = await client.wait_for('message', timeout=60.0, check=check)

        # if user is too slow, let him know
        except asyncio.TimeoutError:
            await msg.edit(embed=embed_message(
                f'Sorry {message.author.display_name}',
                f'You took to long to answer my question, please start over'
            ))
            await asyncio.sleep(60)
            await msg.delete()
            return None, None

        # try to convert the answer to int, else throw error
        else:
            try:
                # check if int
                index = int(answer_msg.content) - 1
                # check if within length
                if (index + 1) > len(data):
                    raise ValueError

                await msg.delete()
                await answer_msg.delete()
            except ValueError:
                await msg.edit(embed=embed_message(
                    f'Sorry {message.author.display_name}',
                    f'{answer_msg.content} is not a valid number. Please start over'
                ))
                await asyncio.sleep(60)
                await msg.delete()
                await answer_msg.delete()
                return None, None

    name = list(data.keys())[index]
    return name, data[name]


# returns all items in bucket. Deafult is vault hash, for others search "bucket" at https://data.destinysets.com/
async def getInventoryBucket(destinyID, bucket=138197802):
    res = (await getProfile(destinyID, 102, with_token=True))
    if not res:
        return None
    items = res["profileInventory"]["data"]["items"]
    ret = []
    print(items)
    for item in items:
        if item["bucketHash"] == bucket:    # vault hash
            ret.append(item)

    return ret


# gets the current artifact, which includes the level
async def getArtifact(destinyID):
    return (await getProfile(destinyID, 104, with_token=True))['profileProgression']['data']['seasonalArtifact']


# returns all items in inventory
async def getCharacterGear(destinyID):
    items = []
    chars = await getCharacterList(destinyID)

    # not equiped on chars
    char_inventory = (await getProfile(destinyID, 201, with_token=True))["characterInventories"]["data"]
    for char in chars[1]:
        items.extend(char_inventory[char]["items"])

    # equiped on chars
    char_inventory = (await getProfile(destinyID, 205))['characterEquipment']["data"]
    for char in chars[1]:
        items.extend(char_inventory[char]["items"])

    return items

async def getCharacterGearAndPower(destinyID):
    items = []
    chars = await getCharacterList(destinyID)

    # not equiped on chars
    playerProfile = (await getProfile(destinyID, 201, 205, 300, with_token=True))
    itempower = {weaponid:int(weapondata.get("primaryStat", {"value":0})['value']) for weaponid, weapondata in playerProfile["itemComponents"]["instances"]["data"].items()}
    itempower['none'] = 0
    for char in chars[1]:
        charitems = playerProfile["characterInventories"]["data"][char]["items"] + playerProfile['characterEquipment']["data"][char]["items"]
        charpoweritems = map(lambda charitem:dict(charitem, **{'lightlevel':itempower[charitem.get('itemInstanceId', 'none')]}), charitems)
        items.extend(charpoweritems)

    return items

# returns all items in vault + inventory. Also gets ships and stuff - not only armor / weapons
async def getAllGear(destinyID):
    # vault
    items = await getInventoryBucket(destinyID)

    items.extend(await getCharacterGear(destinyID))

    # returns a list with the dicts of the items
    return items


# returns list of all copies of that piece
async def getGearPiece(destinyID, itemID):
    items = await getAllGear(destinyID)

    instances = []
    for item in items:
        if item["itemHash"] == itemID:
            instances.append(item)

    return instances


async def getWeaponStats(destinyID, weaponIDs: list, characterID=None, mode=0):
    """ returns kills, prec_kills for that weapon in the specified mode"""

    # get the info from the DB
    result = []
    for weaponID in weaponIDs:
        if characterID:
            result.extend(getWeaponInfo(destinyID, weaponID, characterID=characterID, mode=mode))
        else:
            result.extend(getWeaponInfo(destinyID, weaponID, mode=mode))

    # add stats
    kills = 0
    prec_kills = 0
    for _, k, p_k in result:
        kills += k
        prec_kills += p_k

    return kills, prec_kills


async def getNameToHashMapByClanid(clanid):
    requestURL = "https://www.bungie.net/Platform/GroupV2/{}/members/".format(clanid) #memberlist
    memberJSON = await getJSONfromURL(requestURL)
    if not memberJSON:
        return {} 
    memberlist = memberJSON['Response']['results']
    memberids  = dict()
    for member in memberlist:
        memberids[member['destinyUserInfo']['LastSeenDisplayName']] = member['destinyUserInfo']['membershipId']
    return memberids

async def getNameAndCrossaveNameToHashMapByClanid(clanid):
    requestURL = "https://www.bungie.net/Platform/GroupV2/{}/members/".format(clanid) #memberlist
    memberJSON = await getJSONfromURL(requestURL)
    if not memberJSON:
        return {}
    memberlist = memberJSON['Response']['results']
    memberids  = dict()
    for member in memberlist:
        if 'bungieNetUserInfo' in member.keys():
            memberids[member['destinyUserInfo']['membershipId']] = (member['destinyUserInfo']['LastSeenDisplayName'], member['bungieNetUserInfo']['displayName'])
        else:
            memberids[member['destinyUserInfo']['membershipId']] = (member['destinyUserInfo']['LastSeenDisplayName'], 'none')
    return memberids


async def getPGCR(instanceID):
    return await getJSONfromURL(f'https://www.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{instanceID}/')


# type = "DestinyInventoryItemDefinition" (fe.), hash = 3993415705 (fe)   - returns MT
async def returnManifestInfo(type, hash):
    info = await getJSONfromURL(f'http://www.bungie.net/Platform/Destiny2/Manifest/{type}/{hash}/')

    if info:
        return info
    else:
        return None


async def updateManifest():
    # get the manifest
    manifest_url = 'http://www.bungie.net/Platform/Destiny2/Manifest/'
    manifest = await getJSONfromURL(manifest_url)
    if not manifest:
        print("Couldnt get manifest, aborting")
        return

    print("Starting manifest update...")

    # check if the downloaded version is different to ours, if so drop entries and redownload info
    name = "Manifest"
    version = manifest['Response']['version']
    if version == await getVersion(name):
        return

    # version is different, so re-download:
    # For that we are using a transaction to not disrupt normal bot behaviour
    pool = await get_connection_pool()
    async with pool.acquire() as connection:
        async with connection.transaction():
            # Now Drop all the table entries and then loop through the relevant manifest locations and save them in the DB
            for definition, url in manifest['Response']['jsonWorldComponentContentPaths']['en'].items():
                if definition == "DestinyActivityDefinition":
                    print("Starting DestinyActivityDefinition update...")
                    await deleteEntries(connection, "DestinyActivityDefinition")
                    result = await getJSONfromURL(f'http://www.bungie.net{url}')
                    # update table
                    for referenceId, values in result.items():
                        await updateDestinyDefinition(
                            connection,
                            definition,
                            int(referenceId),
                            description=values["displayProperties"]["description"] if values["displayProperties"]["description"] else None,
                            name=values["displayProperties"]["name"] if values["displayProperties"]["name"] else None,
                            activityLevel=values["activityLevel"] if 'activityLevel' in values else 0,
                            activityLightLevel=values["activityLightLevel"],
                            destinationHash=values["destinationHash"],
                            placeHash=values["placeHash"],
                            activityTypeHash=values["activityTypeHash"],
                            isPvP=values["isPvP"],
                            directActivityModeHash=values["directActivityModeHash"] if "directActivityModeHash" in values else None,
                            directActivityModeType=values["directActivityModeType"] if "directActivityModeType" in values else None,
                            activityModeHashes=values["activityModeHashes"] if "activityModeHashes" in values else None,
                            activityModeTypes=values["activityModeTypes"] if "activityModeTypes" in values else None
                        )

                elif definition == "DestinyActivityTypeDefinition":
                    print("Starting DestinyActivityTypeDefinition update...")
                    await deleteEntries(connection, "DestinyActivityTypeDefinition")
                    result = await getJSONfromURL(f'http://www.bungie.net{url}')
                    # update table
                    for referenceId, values in result.items():
                        await updateDestinyDefinition(
                            connection,
                            definition,
                            int(referenceId),
                            description=values["displayProperties"]["description"] if "displayProperties" in values and "description" in values["displayProperties"] and values["displayProperties"]["description"] else None,
                            name=values["displayProperties"]["name"] if "displayProperties" in values and "name" in values["displayProperties"] and values["displayProperties"]["name"] else None
                        )

                elif definition == "DestinyActivityModeDefinition":
                    print("Starting DestinyActivityModeDefinition update...")
                    await deleteEntries(connection, "DestinyActivityModeDefinition")
                    result = await getJSONfromURL(f'http://www.bungie.net{url}')
                    # update table
                    for referenceId, values in result.items():
                        await updateDestinyDefinition(
                            connection,
                            definition,
                            values["modeType"],
                            description=values["displayProperties"]["description"] if values["displayProperties"]["description"] else None,
                            name=values["displayProperties"]["name"] if values["displayProperties"]["name"] else None,
                            hash=int(referenceId),
                            activityModeCategory=values["activityModeCategory"],
                            isTeamBased=values["isTeamBased"],
                            friendlyName=values["friendlyName"]
                        )

                elif definition == "DestinyCollectibleDefinition":
                    print("Starting DestinyCollectibleDefinition update...")
                    await deleteEntries(connection, "DestinyCollectibleDefinition")
                    result = await getJSONfromURL(f'http://www.bungie.net{url}')
                    # update table
                    for referenceId, values in result.items():
                        await updateDestinyDefinition(
                            connection,
                            definition,
                            int(referenceId),
                            description=values["displayProperties"]["description"] if values["displayProperties"]["description"] else None,
                            name=values["displayProperties"]["name"] if values["displayProperties"]["name"] else None,
                            sourceHash=values["sourceHash"] if "sourceHash" in values else None,
                            itemHash=values["itemHash"] if "itemHash" in values else None,
                            parentNodeHashes=values["parentNodeHashes"] if "parentNodeHashes" in values else None
                        )

                elif definition == "DestinyInventoryItemDefinition":
                    print("Starting DestinyInventoryItemDefinition update...")
                    await deleteEntries(connection, "DestinyInventoryItemDefinition")
                    result = await getJSONfromURL(f'http://www.bungie.net{url}')
                    # update table
                    for referenceId, values in result.items():
                        await updateDestinyDefinition(
                            connection,
                            definition,
                            int(referenceId),
                            description=values["displayProperties"]["description"] if values["displayProperties"]["description"] else None,
                            name=values["displayProperties"]["name"] if values["displayProperties"]["name"] else None,
                            classType=values["classType"] if "classType" in values else None,
                            bucketTypeHash=values["inventory"]["bucketTypeHash"],
                            tierTypeHash=values["inventory"]["tierTypeHash"],
                            tierTypeName=values["inventory"]["tierTypeName"] if "tierTypeName" in values["inventory"] else None,
                            equippable=values["equippable"]
                        )

                elif definition == "DestinyRecordDefinition":
                    print("Starting DestinyRecordDefinition update...")
                    await deleteEntries(connection, "DestinyRecordDefinition")
                    result = await getJSONfromURL(f'http://www.bungie.net{url}')
                    # update table
                    for referenceId, values in result.items():
                        await updateDestinyDefinition(
                            connection,
                            definition,
                            int(referenceId),
                            description=values["displayProperties"]["description"] if values["displayProperties"]["description"] else None,
                            name=values["displayProperties"]["name"] if values["displayProperties"]["name"] else None,
                            hasTitle=values["titleInfo"]["hasTitle"],
                            titleName=values["titleInfo"]["titlesByGender"]["Male"] if "titlesByGender" in values["titleInfo"] else None,
                            objectiveHashes=values["objectiveHashes"] if "objectiveHashes" in values else None,
                            ScoreValue=values["completionInfo"]["ScoreValue"] if "completionInfo" in values else None,
                            parentNodeHashes=values["parentNodeHashes"] if "parentNodeHashes" in values else None
                        )

                elif definition == "DestinyInventoryBucketDefinition":
                    print("Starting DestinyInventoryBucketDefinition update...")
                    await deleteEntries(connection, "DestinyInventoryBucketDefinition")
                    result = await getJSONfromURL(f'http://www.bungie.net{url}')
                    # update table
                    for referenceId, values in result.items():
                        await updateDestinyDefinition(
                            connection,
                            definition,
                            int(referenceId),
                            description=values["displayProperties"]["description"] if "description" in values["displayProperties"] else None,
                            name=values["displayProperties"]["name"] if "name" in values["displayProperties"] else None,
                            category=values["category"],
                            itemCount=values["itemCount"],
                            location=values["location"]
                        )

    # update version entry
    await updateVersion(name, version)

    print("Done with manifest update!")


async def insertPgcrToDB(instanceID: int, activity_time: datetime, pcgr: dict):
    """ Saves the specified PGCR data in the DB """
    insertPgcrActivities(
        instanceID,
        pcgr["activityDetails"]["referenceId"],
        pcgr["activityDetails"]["directorActivityHash"],
        activity_time,
        pcgr["startingPhaseIndex"],
        pcgr["activityDetails"]["mode"],
        pcgr["activityDetails"]["modes"],
        pcgr["activityDetails"]["isPrivate"],
        pcgr["activityDetails"]["membershipType"]
    )

    # loop though user and save info to db
    for user_pcgr in pcgr["entries"]:
        characterID = user_pcgr["characterId"]
        membershipID = user_pcgr["player"]["destinyUserInfo"]["membershipId"]

        insertPgcrActivitiesUsersStats(
            instanceID,
            membershipID,
            characterID,
            user_pcgr["player"]["characterClass"] if "characterClass" in user_pcgr["player"] else "",
            user_pcgr["player"]["characterLevel"],
            user_pcgr["player"]["destinyUserInfo"]["membershipType"],
            user_pcgr["player"]["lightLevel"],
            user_pcgr["player"]["emblemHash"],
            user_pcgr["standing"],
            int(user_pcgr["values"]["assists"]["basic"]["value"]),
            int(user_pcgr["values"]["completed"]["basic"]["value"]),
            int(user_pcgr["values"]["deaths"]["basic"]["value"]),
            int(user_pcgr["values"]["kills"]["basic"]["value"]),
            int(user_pcgr["values"]["opponentsDefeated"]["basic"]["value"]),
            user_pcgr["values"]["efficiency"]["basic"]["value"],
            user_pcgr["values"]["killsDeathsRatio"]["basic"]["value"],
            user_pcgr["values"]["killsDeathsAssists"]["basic"]["value"],
            int(user_pcgr["values"]["score"]["basic"]["value"]),
            int(user_pcgr["values"]["activityDurationSeconds"]["basic"]["value"]),
            int(user_pcgr["values"]["completionReason"]["basic"]["value"]),
            int(user_pcgr["values"]["startSeconds"]["basic"]["value"]),
            int(user_pcgr["values"]["timePlayedSeconds"]["basic"]["value"]),
            int(user_pcgr["values"]["playerCount"]["basic"]["value"]),
            int(user_pcgr["values"]["teamScore"]["basic"]["value"]),
            int(user_pcgr["extended"]["values"]["precisionKills"]["basic"]["value"]),
            int(user_pcgr["extended"]["values"]["weaponKillsGrenade"]["basic"]["value"]),
            int(user_pcgr["extended"]["values"]["weaponKillsMelee"]["basic"]["value"]),
            int(user_pcgr["extended"]["values"]["weaponKillsSuper"]["basic"]["value"]),
            int(user_pcgr["extended"]["values"]["weaponKillsAbility"]["basic"]["value"])
        )

        # loop though each weapon and save that info in the DB
        if "weapons" in user_pcgr["extended"]:
            for weapon_user_pcgr in user_pcgr["extended"]["weapons"]:
                insertPgcrActivitiesUsersStatsWeapons(
                    instanceID,
                    characterID,
                    membershipID,
                    weapon_user_pcgr["referenceId"],
                    int(weapon_user_pcgr["values"]["uniqueWeaponKills"]["basic"]["value"]),
                    int(weapon_user_pcgr["values"]["uniqueWeaponPrecisionKills"]["basic"]["value"])
                )


async def updateDB(destinyID):
    """ Gets this users not-saved history and saves it """
    async def handle(instanceID, activity_time):
        # get PGCR
        pcgr = await getPGCR(instanceID)
        if not pcgr:
            print('Failed getting pcgr <%s>. Trying again later', instanceID)
            insertFailToGetPgcrInstanceId(instanceID, activity_time)
            logger.warning('Failed getting pcgr <%s>', instanceID)
            return None
        return [instanceID, activity_time, pcgr["Response"]]

    async def input_data(gather_instanceID, gather_activity_time):
        result = await asyncio.gather(*[handle(instanceID, activity_time) for instanceID, activity_time in zip(gather_instanceID, gather_activity_time)])

        for res in result:
            if res is not None:

                instanceID = res[0]
                activity_time = res[1]
                pcgr = res[2]

                # insert information to DB
                await insertPgcrToDB(instanceID, activity_time, pcgr)
                #print(f'inserted instance {instanceID}')

    logger = logging.getLogger('updateDB')
    entry_time = getLastUpdated(destinyID)

    logger.info('Starting activity DB update for destinyID <%s>', destinyID)

    gather_instanceID = []
    gather_activity_time = []
    async for activity in getPlayersPastActivities(destinyID, mode=0, earliest_allowed_time=entry_time):
        instanceID = activity["activityDetails"]["instanceId"]
        activity_time = datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ")

        # update with newest entry timestamp
        if activity_time > entry_time:
            entry_time = activity_time

        # check if info is already in DB, skip if so
        if getPgcrActivity(instanceID):
            continue

        # add to gather list
        gather_instanceID.append(instanceID)
        gather_activity_time.append(activity_time)

        # gather once list is big enough
        if len(gather_instanceID) < 50:
            continue
        else:
            # get and input the data
            await input_data(gather_instanceID, gather_activity_time)

            # reset gather list and restart
            gather_instanceID = []
            gather_activity_time = []

    # one last time to clean out the extras after the code is done
    if gather_instanceID:
        # get and input the data
        await input_data(gather_instanceID, gather_activity_time)

    # update with newest entry timestamp
    updateLastUpdated(destinyID, entry_time)

    logger.info('Done with activity DB update for destinyID <%s>', destinyID)


async def updateMissingPcgr():
    # this gets called after a lot of requests, relaxing bungie first
    await asyncio.sleep(30)

    for missing in getFailToGetPgcrInstanceId():
        instanceID = missing[0]
        activity_time = missing[1]

        # check if info is already in DB, delete and skip if so
        if getPgcrActivity(instanceID):
            deleteFailToGetPgcrInstanceId(instanceID)
            continue

        # get PGCR
        pcgr = await getPGCR(instanceID)

        # only continue if we get a response this time
        if not pcgr:
            continue

        # add info to DB
        pcgr = pcgr["Response"]
        await insertPgcrToDB(instanceID, activity_time, pcgr)

        # delete from to-do DB
        deleteFailToGetPgcrInstanceId(instanceID)


async def getClanMembers(client):
    # get all clan members {destinyID: discordID}
    memberlist = {}
    for member in (await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"))["Response"][
        "results"]:
        destinyID = int(member["destinyUserInfo"]["membershipId"])
        discordID = lookupDiscordID(destinyID)
        if discordID is not None:
            memberlist.update({destinyID: discordID})

    return memberlist


#TODO replace with DB and version checks

