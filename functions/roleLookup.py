from datetime import datetime

import discord
import asyncio
import time

from functions.database import getFlawlessHashes, getClearCount, getDestinyDefinition
from functions.dataTransformation import hasLowman
from functions.dataTransformation import hasCollectible, hasTriumph
from static.dict import requirementHashes
# check if user has permission to use this command
from static.globals import role_ban_id

#TODO remove year parameter
async def hasRole(playerid, role, year, br = True):
    """ br may be set to True if only True/False is exptected, set to False to get complete data on why or why not the user earned the role """
    data = {}

    roledata = requirementHashes[year][role]
    if not 'requirements' in roledata:
        print('malformatted requirementHashes')
        return [False, data]
    worthy = True
    start_reqs = time.monotonic()
    for req in roledata['requirements']:
        if req == 'clears':
            creq = roledata['clears']
            i = 1
            for raid in creq:
                actualclears = getClearCount(playerid, raid['actHashes'])
                if not actualclears>= raid['count']:
                    #print(f'{playerid} is only has {actualclears} out of {raid["count"]} for {",".join([str(x) for x in raid["actHashes"]])}')
                    worthy = False

                data["Clears #" + str(i)] = str(actualclears) + " / " + str(raid['count'])
                i += 1

        elif req == 'flawless':
            has_fla = bool(getFlawlessHashes(playerid, roledata['flawless']))
            worthy &= has_fla

            data["Flawless"] = bool(has_fla)

        elif req == 'collectibles':
            for collectibleHash in roledata['collectibles']:
                has_coll_start = time.monotonic()
                has_col = await hasCollectible(playerid, collectibleHash)
                has_coll_end = time.monotonic()
                if (diff := has_coll_end - has_coll_start) > 1:
                    print(f'hasCollectible took {diff} seconds')
                worthy &= has_col

                if (not worthy) and br:
                    break
                
                if not br:
                    # get name of collectible
                    name = "No name here"
                    #str conversion required because dictionary is indexed on strings, not postiions
                    coll_def_start = time.monotonic()
                    (_, _, name, *_) = getDestinyDefinition("DestinyCollectibleDefinition", collectibleHash)
                    coll_def_end = time.monotonic()
                    if (diff := coll_def_end - coll_def_start) > 1:
                        print(f'getDestinyDefinition in collectibles took {diff} seconds')
                    data[name] = bool(has_col)

        elif req == 'records':
            start_records = time.time()
            for recordHash in roledata['records']:
                start_record_sub = time.time()
                has_tri = await hasTriumph(playerid, recordHash)
                worthy &= has_tri

                if (not worthy) and br:
                    break
                
                if not br:
                    # get name of triumph
                    name = "No name here"
                    (_, _, name, *_) = getDestinyDefinition("DestinyRecordDefinition", recordHash)
                    data[name] = bool(has_tri)
                    
                end_record_sub = time.time() - start_record_sub
                if end_record_sub > 1:
                    #print(f'took {end_record_sub} seconds to check record {recordHash}')
                    pass
            end_records = time.time() - start_records
            if end_records > 1:
                #print(f'took {end_records} seconds to check records for {role}')
                pass
        elif req == 'lowman':
            start_lowman_reqs = time.monotonic()
            denies = sum([1 if 'denyTime' in key else 0 for key in roledata.keys()])
            timeParse = lambda i, spec: datetime.strptime(roledata[f'denyTime{i}'][spec], "%d/%m/%Y %H:%M")
            disallowed = [(timeParse(i, 'startTime'), timeParse(i, 'endTime')) for i in range(denies)]
            end_lowman_reqs = time.monotonic()
            if (diff := end_lowman_reqs - start_lowman_reqs) > 1:
                print(f'Lowman Requirements took {diff} seconds for disallowed times')
            start_lowman_read = time.monotonic()
            has_low = await hasLowman(
                playerid,
                roledata['playercount'],
                roledata['activityHashes'],
                flawless=roledata.get('flawless', False),
                score_threshold=roledata.get('score', False),
                noCheckpoints=roledata.get('noCheckpoints', False),
                disallowed=disallowed
            )
            worthy &= has_low

            data["Lowman (" + str(roledata['playercount']) + " Players)"] = bool(has_low)
            end_lowman_read = time.monotonic()
            if (diff := end_lowman_read - start_lowman_read) > 1:
                print(f'Lowman Read took {diff} seconds for hasLowman')
        elif req == 'roles':
            for required_role in roledata['roles']:
                req_worthy, req_data = await hasRole(playerid, required_role, year, br=br)
                worthy &= req_worthy #only worthy if worthy for all required roles
                data = {**req_data, **data} #merging dicts, data dominates
                data[f'Role: {required_role}'] = bool(req_worthy)

        if (not worthy) and br:
            break
    end_reqs = time.monotonic() - start_reqs
    if end_reqs > 1:
        print(f'took {end_reqs} seconds to check requirements for {role}')
    return [worthy, data]

async def getPlayerRoles(playerid, existingRoles = []):
    if not playerid:
        print('got empty playerid')
        return ([],[])
    print(f'getting roles for {playerid}')
    roles = []
    redundantRoles = []

    for year, yeardata in requirementHashes.items():
        for role, roledata in yeardata.items():
            #do not recheck existing roles or roles that will be replaced by existing roles
            if role in existingRoles or ('replaced_by' in roledata.keys() and any([x in existingRoles for x in roledata['replaced_by']])):
                roles.append(role)
    
    # asyncio.gather keeps order
    roleyear_to_check = [
        (role, year)
        for (year, yeardata) in requirementHashes.items() 
        for role in yeardata.keys()
        if not role in roles
    ]

    # check worthyness in parallel
    starttime = time.time()
    has_earned_role = await asyncio.gather(*[
        hasRole(playerid, role, year) 
        for (role, year) in roleyear_to_check
    ])
    endtime = time.time() - starttime
    print(f'took {endtime} seconds to gather hasRoles')

    roles.extend([rolename for ((rolename, roleyear), (isworthy, worthydetails)) in zip(roleyear_to_check, has_earned_role) if isworthy])


    #remove roles that are replaced by others
    for yeardata in requirementHashes.values():
        for roleName, roledata in yeardata.items():
            if roleName not in roles:
                redundantRoles.append(roleName)
            if 'replaced_by' in roledata.keys():
                for superior in roledata['replaced_by']:
                    if superior in roles:
                        if roleName in roles:
                            roles.remove(roleName)
                            redundantRoles.append(roleName)
    
    return (roles, redundantRoles)

async def assignRolesToUser(roleList, discordUser, guild, reason=None):
    #takes rolelist as string array, userSnowflake, guild object
    if not discordUser:
        return False
    
    role_banned = discord.utils.get(guild.roles, name='Role Banned') or discord.utils.get(guild.roles, id=role_ban_id)
    if role_banned in discordUser.roles:
        return False

    for role in roleList:
        #print(guild.roles)
        roleObj = discord.utils.get(guild.roles, name=role) or discord.utils.get(guild.roles, id=role)
        if not roleObj:
            if guild.id in [669293365900214293]: #We only care about the descend discord
                print(f'assignable role doesn\'t exist in {guild.name} with id {guild.id}: {role}')
            continue
        if roleObj not in discordUser.roles:
            try:
                await discordUser.add_roles(roleObj, reason=reason)
                print(f'added role {roleObj.name} to user {discordUser.name} in server {guild.name}')
            except discord.errors.Forbidden:
                print(f'failed to add {roleObj.name} to user {discordUser.name} in server {guild.name}')
                return False
    return True

async def removeRolesFromUser(roleStringList, discordUser, guild, reason=None):
    removeRolesObjs = []
    for role in roleStringList:
        roleObj = discord.utils.get(guild.roles, name=role) or discord.utils.get(guild.roles, id=role)
        if roleObj is None and guild.id not in [556418279015448596, 724676552175910934]:
            print(f'removeable role doesn\'t exist: {role}')
            continue
        removeRolesObjs.append(roleObj)
    for roleObj in removeRolesObjs:
        #print(f'removed {roleObj.name} from {discordUser.name}')
        if roleObj in discordUser.roles:
            print(f'removed role {roleObj.name} from user {discordUser.name}')
            try:
                await discordUser.remove_roles(roleObj, reason=reason)
            except discord.errors.Forbidden:
                return False
    return True