import asyncio
from datetime import datetime

from ElevatorBot.database.database import (
    get_connection_pool,
    lookupDiscordID,
    insertPgcrActivities,
    getPgcrActivity,
    insertPgcrActivitiesUsersStats,
    insertPgcrActivitiesUsersStatsWeapons,
    getFailToGetPgcrInstanceId,
    deleteFailToGetPgcrInstanceId,
    updateDestinyDefinition,
    getVersion,
    updateVersion,
    deleteEntries,
)
from ElevatorBot.core.formating import embed_message
from ElevatorBot.networking.models import WebResponse
from ElevatorBot.networking.network import get_json_from_url
from ElevatorBot.static.config import CLANID
from ElevatorBot.static.dict import weaponTypeKinetic, weaponTypeEnergy, weaponTypePower


# gets the weapon (name, [hash1, hash2, ...]) for the search term for all weapons found
# more than one weapon can be found if it got reissued
async def searchForItem(ctx, search_term):
    # search for the weapon in the api
    info = await get_json_from_url(
        f"http://www.bungie.net/Platform/Destiny2/Armory/Search/DestinyInventoryItemDefinition/{search_term}/"
    )
    data = {}
    try:
        for weapon in info.content["Response"]["results"]["results"]:
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
        await ctx.send(
            hidden=True,
            embed=embed_message(
                f"Error",
                f"I do not know the weapon `{search_term}`. \nPlease try again",
            ),
        )
        return None, None

    # defer now that we know the weapon exists
    if not ctx.deferred:
        await ctx.defer()

    # check if we found multiple items with different names. Ask user to specify which one is correct
    index = 0
    if len(data) > 1:
        # asking user for the correct item
        text = "Multiple items can be found with that search term, please specify which item you meant by sending the corresponding number:\n\u200B"
        i = 1
        for name in data.keys():
            text += f"\n**{i}** - {name}"
            i += 1
        msg = await ctx.channel.send(embed=embed_message(f"{ctx.author.display_name}, I need one more thing", text))

        # to check whether or not the one that send the msg is the original author for the function after this
        def check(answer_msg):
            return answer_msg.author == ctx.author and answer_msg.channel == ctx.channel

        # wait for reply from original user to set the time parameters
        try:
            answer_msg = await ctx.bot.wait_for("message", timeout=60.0, check=check)

        # if user is too slow, let him know
        except asyncio.TimeoutError:
            await ctx.send(
                embed=embed_message(
                    f"Sorry {ctx.author.display_name}",
                    f"You took to long to answer my question, please start over",
                )
            )
            await msg._delete()
            return None, None

        # try to convert the answer to int, else throw error
        else:
            try:
                # check if int
                index = int(answer_msg.content) - 1
                # check if within length
                if (index + 1) > len(data):
                    raise ValueError

                await msg._delete()
                await answer_msg._delete()
            except ValueError:
                await msg._delete()
                await answer_msg._delete()
                await ctx.send(
                    embed=embed_message(
                        f"Sorry {ctx.author.display_name}",
                        f"{answer_msg.content} is not a valid number. Please start over",
                    )
                )
                return None, None

    name = list(data.keys())[index]
    return name, data[name]


async def getNameToHashMapByClanid(clanid):
    requestURL = "https://www.bungie.net/Platform/GroupV2/{}/members/".format(clanid)  # memberlist
    memberJSON = await get_json_from_url(requestURL)
    if not memberJSON:
        return {}
    memberlist = memberJSON.content["Response"]["results"]
    memberids = dict()
    for member in memberlist:
        memberids[member["destinyUserInfo"]["LastSeenDisplayName"]] = member["destinyUserInfo"]["membershipId"]
    return memberids


async def getNameAndCrossaveNameToHashMapByClanid(clanid):
    requestURL = "https://www.bungie.net/Platform/GroupV2/{}/members/".format(clanid)  # memberlist
    memberJSON = await get_json_from_url(requestURL)
    if not memberJSON:
        return {}
    memberlist = memberJSON.content["Response"]["results"]
    memberids = dict()
    for member in memberlist:
        if "bungieNetUserInfo" in member.keys():
            memberids[member["destinyUserInfo"]["membershipId"]] = (
                member["destinyUserInfo"]["LastSeenDisplayName"],
                member["bungieNetUserInfo"]["displayName"],
            )
        else:
            memberids[member["destinyUserInfo"]["membershipId"]] = (
                member["destinyUserInfo"]["LastSeenDisplayName"],
                "none",
            )
    return memberids


# async def get_pgcr(instance_id: int) -> WebResponse:
#     return await get_json_from_url(
#         f"https://www.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{instance_id}/"
#     )


# async def updateManifest():
#     # get the manifest
#     manifest_url = "http://www.bungie.net/Platform/Destiny2/Manifest/"
#     manifest = await get(manifest_url)
#     if not manifest:
#         print("Couldnt get manifest, aborting")
#         return
#
#     # check if the downloaded version is different to ours, if so drop entries and redownload info
#     name = "Manifest"
#     version = manifest.content["Response"]["version"]
#     if version == await getVersion(name):
#         return
#
#     print("Starting manifest _update...")
#
#     # version is different, so re-download:
#     # For that we are using a transaction to not disrupt normal bot behaviour
#     pool = await get_connection_pool()
#     async with pool.acquire() as connection:
#         async with connection.transaction():
#             # Now Drop all the table entries and then loop through the relevant manifest locations and save them in the DB
#             for definition, url in manifest.content["Response"]["jsonWorldComponentContentPaths"]["en"].items():
#                 if definition == "DestinyActivityDefinition":
#                     print("Starting DestinyActivityDefinition _update...")
#                     await deleteEntries(connection, "DestinyActivityDefinition")
#                     result = await get(f"http://www.bungie.net{url}")
#                     # _update table
#                     for referenceId, values in result.content.items():
#                         await updateDestinyDefinition(
#                             connection,
#                             definition,
#                             int(referenceId),
#                             description=values["displayProperties"]["description"]
#                             if values["displayProperties"]["description"]
#                             else None,
#                             name=values["displayProperties"]["name"] if values["displayProperties"]["name"] else None,
#                             activityLevel=values["activityLevel"] if "activityLevel" in values else 0,
#                             activityLightLevel=values["activityLightLevel"],
#                             destinationHash=values["destinationHash"],
#                             placeHash=values["placeHash"],
#                             activityTypeHash=values["activityTypeHash"],
#                             isPvP=values["isPvP"],
#                             directActivityModeHash=values["directActivityModeHash"]
#                             if "directActivityModeHash" in values
#                             else None,
#                             directActivityModeType=values["directActivityModeType"]
#                             if "directActivityModeType" in values
#                             else None,
#                             activityModeHashes=values["activityModeHashes"] if "activityModeHashes" in values else None,
#                             activityModeTypes=values["activityModeTypes"] if "activityModeTypes" in values else None,
#                         )
#
#                 elif definition == "DestinyActivityTypeDefinition":
#                     print("Starting DestinyActivityTypeDefinition _update...")
#                     await deleteEntries(connection, "DestinyActivityTypeDefinition")
#                     result = await get(f"http://www.bungie.net{url}")
#                     # _update table
#                     for referenceId, values in result.content.items():
#                         await updateDestinyDefinition(
#                             connection,
#                             definition,
#                             int(referenceId),
#                             description=values["displayProperties"]["description"]
#                             if "displayProperties" in values
#                             and "description" in values["displayProperties"]
#                             and values["displayProperties"]["description"]
#                             else None,
#                             name=values["displayProperties"]["name"]
#                             if "displayProperties" in values
#                             and "name" in values["displayProperties"]
#                             and values["displayProperties"]["name"]
#                             else None,
#                         )
#
#                 elif definition == "DestinyActivityModeDefinition":
#                     print("Starting DestinyActivityModeDefinition _update...")
#                     await deleteEntries(connection, "DestinyActivityModeDefinition")
#                     result = await get(f"http://www.bungie.net{url}")
#                     # _update table
#                     for referenceId, values in result.content.items():
#                         await updateDestinyDefinition(
#                             connection,
#                             definition,
#                             values["modeType"],
#                             description=values["displayProperties"]["description"]
#                             if values["displayProperties"]["description"]
#                             else None,
#                             name=values["displayProperties"]["name"] if values["displayProperties"]["name"] else None,
#                             hash=int(referenceId),
#                             activityModeCategory=values["activityModeCategory"],
#                             isTeamBased=values["isTeamBased"],
#                             friendlyName=values["friendlyName"],
#                         )
#
#                 elif definition == "DestinyCollectibleDefinition":
#                     print("Starting DestinyCollectibleDefinition _update...")
#                     await deleteEntries(connection, "DestinyCollectibleDefinition")
#                     result = await get(f"http://www.bungie.net{url}")
#                     # _update table
#                     for referenceId, values in result.content.items():
#                         await updateDestinyDefinition(
#                             connection,
#                             definition,
#                             int(referenceId),
#                             description=values["displayProperties"]["description"]
#                             if values["displayProperties"]["description"]
#                             else None,
#                             name=values["displayProperties"]["name"] if values["displayProperties"]["name"] else None,
#                             sourceHash=values["sourceHash"] if "sourceHash" in values else None,
#                             itemHash=values["itemHash"] if "itemHash" in values else None,
#                             parentNodeHashes=values["parentNodeHashes"] if "parentNodeHashes" in values else None,
#                         )
#
#                 elif definition == "DestinyInventoryItemDefinition":
#                     print("Starting DestinyInventoryItemDefinition _update...")
#                     await deleteEntries(connection, "DestinyInventoryItemDefinition")
#                     result = await get(f"http://www.bungie.net{url}")
#                     # _update table
#                     for referenceId, values in result.content.items():
#                         await updateDestinyDefinition(
#                             connection,
#                             definition,
#                             int(referenceId),
#                             description=values["displayProperties"]["description"]
#                             if values["displayProperties"]["description"]
#                             else None,
#                             name=values["displayProperties"]["name"] if values["displayProperties"]["name"] else None,
#                             classType=values["classType"] if "classType" in values else None,
#                             bucketTypeHash=values["inventory"]["bucketTypeHash"],
#                             tierTypeHash=values["inventory"]["tierTypeHash"],
#                             tierTypeName=values["inventory"]["tierTypeName"]
#                             if "tierTypeName" in values["inventory"]
#                             else None,
#                             equippable=values["equippable"],
#                         )
#
#                 elif definition == "DestinyRecordDefinition":
#                     print("Starting DestinyRecordDefinition _update...")
#                     await deleteEntries(connection, "DestinyRecordDefinition")
#                     result = await get(f"http://www.bungie.net{url}")
#                     # _update table
#                     for referenceId, values in result.content.items():
#                         await updateDestinyDefinition(
#                             connection,
#                             definition,
#                             int(referenceId),
#                             description=values["displayProperties"]["description"]
#                             if values["displayProperties"]["description"]
#                             else None,
#                             name=values["displayProperties"]["name"] if values["displayProperties"]["name"] else None,
#                             hasTitle=values["titleInfo"]["hasTitle"],
#                             titleName=values["titleInfo"]["titlesByGender"]["Male"]
#                             if "titlesByGender" in values["titleInfo"]
#                             else None,
#                             objectiveHashes=values["objectiveHashes"] if "objectiveHashes" in values else None,
#                             ScoreValue=values["completionInfo"]["ScoreValue"] if "completionInfo" in values else None,
#                             parentNodeHashes=values["parentNodeHashes"] if "parentNodeHashes" in values else None,
#                         )
#
#                 elif definition == "DestinyInventoryBucketDefinition":
#                     print("Starting DestinyInventoryBucketDefinition _update...")
#                     await deleteEntries(connection, "DestinyInventoryBucketDefinition")
#                     result = await get(f"http://www.bungie.net{url}")
#                     # _update table
#                     for referenceId, values in result.content.items():
#                         await updateDestinyDefinition(
#                             connection,
#                             definition,
#                             int(referenceId),
#                             description=values["displayProperties"]["description"]
#                             if "description" in values["displayProperties"]
#                             else None,
#                             name=values["displayProperties"]["name"] if "name" in values["displayProperties"] else None,
#                             category=values["category"],
#                             itemCount=values["itemCount"],
#                             location=values["location"],
#                         )
#
#                 elif definition == "DestinyPresentationNodeDefinition":
#                     print("Starting DestinyPresentationNodeDefinition _update...")
#                     await deleteEntries(connection, "DestinyPresentationNodeDefinition")
#                     result = await get(f"http://www.bungie.net{url}")
#                     # _update table
#                     for referenceId, values in result.content.items():
#                         await updateDestinyDefinition(
#                             connection,
#                             definition,
#                             int(referenceId),
#                             description=values["displayProperties"]["description"]
#                             if "description" in values["displayProperties"]
#                             else None,
#                             name=values["displayProperties"]["name"] if "name" in values["displayProperties"] else None,
#                             objectiveHash=values["objectiveHash"] if "objectiveHash" in values else None,
#                             presentationNodeType=values["presentationNodeType"],
#                             childrenPresentationNodeHash=[
#                                 list(x.values())[0] for x in values["children"]["presentationNodes"]
#                             ]
#                             if "children" in values and values["children"]["presentationNodes"]
#                             else None,
#                             childrenCollectibleHash=[list(x.values())[0] for x in values["children"]["collectibles"]]
#                             if "children" in values and values["children"]["collectibles"]
#                             else None,
#                             childrenRecordHash=[list(x.values())[0] for x in values["children"]["records"]]
#                             if "children" in values and values["children"]["records"]
#                             else None,
#                             childrenMetricHash=[list(x.values())[0] for x in values["children"]["metrics"]]
#                             if "children" in values and values["children"]["metrics"]
#                             else None,
#                             parentNodeHashes=values["parentNodeHashes"] if "parentNodeHashes" in values else None,
#                             index=values["index"],
#                             redacted=values["redacted"],
#                         )
#
#     # _update version entry
#     await updateVersion(name, version)
#
#     print("Done with manifest _update!")


# async def insertPgcrToDB(instanceID: int, activity_time: datetime, pcgr: dict):
#     """Saves the specified PGCR data in the DB"""
#     await insertPgcrActivities(
#         instanceID,
#         pcgr["activityDetails"]["referenceId"],
#         pcgr["activityDetails"]["directorActivityHash"],
#         activity_time,
#         pcgr["startingPhaseIndex"],
#         pcgr["activityDetails"]["mode"],
#         pcgr["activityDetails"]["modes"],
#         pcgr["activityDetails"]["isPrivate"],
#         pcgr["activityDetails"]["membershipType"],
#     )
#
#     # loop though user and save info to db
#     for user_pcgr in pcgr["entries"]:
#         characterID = user_pcgr["characterId"]
#         membershipID = user_pcgr["player"]["destinyUserInfo"]["membershipId"]
#
#         await insertPgcrActivitiesUsersStats(
#             instanceID,
#             membershipID,
#             characterID,
#             user_pcgr["player"]["characterClass"] if "characterClass" in user_pcgr["player"] else "",
#             user_pcgr["player"]["characterLevel"],
#             user_pcgr["player"]["destinyUserInfo"]["membershipType"],
#             user_pcgr["player"]["lightLevel"],
#             user_pcgr["player"]["emblemHash"],
#             user_pcgr["standing"],
#             int(user_pcgr["values"]["assists"]["basic"]["value"]),
#             int(user_pcgr["values"]["completed"]["basic"]["value"]),
#             int(user_pcgr["values"]["deaths"]["basic"]["value"]),
#             int(user_pcgr["values"]["kills"]["basic"]["value"]),
#             int(user_pcgr["values"]["opponentsDefeated"]["basic"]["value"]),
#             user_pcgr["values"]["efficiency"]["basic"]["value"],
#             user_pcgr["values"]["killsDeathsRatio"]["basic"]["value"],
#             user_pcgr["values"]["killsDeathsAssists"]["basic"]["value"],
#             int(user_pcgr["values"]["score"]["basic"]["value"]),
#             int(user_pcgr["values"]["activityDurationSeconds"]["basic"]["value"]),
#             int(user_pcgr["values"]["completionReason"]["basic"]["value"]),
#             int(user_pcgr["values"]["startSeconds"]["basic"]["value"]),
#             int(user_pcgr["values"]["timePlayedSeconds"]["basic"]["value"]),
#             int(user_pcgr["values"]["playerCount"]["basic"]["value"]),
#             int(user_pcgr["values"]["teamScore"]["basic"]["value"]),
#             int(user_pcgr["extended"]["values"]["precisionKills"]["basic"]["value"]),
#             int(user_pcgr["extended"]["values"]["weaponKillsGrenade"]["basic"]["value"]),
#             int(user_pcgr["extended"]["values"]["weaponKillsMelee"]["basic"]["value"]),
#             int(user_pcgr["extended"]["values"]["weaponKillsSuper"]["basic"]["value"]),
#             int(user_pcgr["extended"]["values"]["weaponKillsAbility"]["basic"]["value"]),
#         )
#
#         # loop though each weapon and save that info in the DB
#         if "weapons" in user_pcgr["extended"]:
#             for weapon_user_pcgr in user_pcgr["extended"]["weapons"]:
#                 await insertPgcrActivitiesUsersStatsWeapons(
#                     instanceID,
#                     characterID,
#                     membershipID,
#                     weapon_user_pcgr["referenceId"],
#                     int(weapon_user_pcgr["values"]["uniqueWeaponKills"]["basic"]["value"]),
#                     int(weapon_user_pcgr["values"]["uniqueWeaponPrecisionKills"]["basic"]["value"]),
#                 )


# async def updateMissingPcgr():
#     # this gets called after a lot of requests, relaxing bungie first
#     await asyncio.sleep(30)
#
#     for (instanceID, activity_time) in await getFailToGetPgcrInstanceId():
#         # instanceID = missing[0]
#         # activity_time = missing[1]
#
#         # check if info is already in DB, _delete and skip if so
#         if await getPgcrActivity(instanceID):
#             await deleteFailToGetPgcrInstanceId(instanceID)
#             continue
#
#         # get PGCR
#         pcgr = await get_pgcr(instanceID)
#
#         # only continue if we get a response this time
#         if not pcgr:
#             continue
#
#         # add info to DB
#         pcgr = pcgr.content["Response"]
#         await insertPgcrToDB(instanceID, activity_time, pcgr)
#
#         # _delete from to-do DB
#         await deleteFailToGetPgcrInstanceId(instanceID)


# async def getClanMembers(client):
#     # get all clan members {destinyID: discordID}
#     memberlist = {}
#     for member in (await get_json_from_url(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/")).content[
#         "Response"
#     ]["results"]:
#         destinyID = int(member["destinyUserInfo"]["membershipId"])
#         discordID = await lookupDiscordID(destinyID)
#         if discordID is not None:
#             memberlist.update({destinyID: discordID})
#
#     return memberlist


def translateWeaponSlot(weapon_slot: int) -> str:
    """Returns weapon_slot as a string"""

    slot = {
        weaponTypeKinetic: "Kinetic",
        weaponTypeEnergy: "Energy",
        weaponTypePower: "Power",
    }

    return slot[weapon_slot]
