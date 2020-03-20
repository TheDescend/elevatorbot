from functions.dataTransformation   import hasFlawless, hasCollectible, hasTriumph
from functions.dataTransformation   import getPlayerCount, getPlayersPastPVE, getClearCount, hasLowman

from static.dict                    import requirementHashes

from datetime           import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import discord

def hasRole(playerid, role, year):
    roledata = requirementHashes[year][role]
    if not 'requirements' in roledata:
        print('malformatted requirementHashes')
        return False
    worthy = True
    for req in roledata['requirements']:
        if req == 'clears':
            creq = roledata['clears']
            for raid in creq:
                if not getClearCount(playerid, raid['actHashes']) >= raid['count']:
                    worthy = False
        elif req == 'flawless':
            worthy &= hasFlawless(playerid, roledata['flawless'])
        elif req == 'collectibles':
            for collectible in roledata['collectibles']:
                worthy &= hasCollectible(playerid, collectible)
        elif req == 'records':
            for recordHash in roledata['records']:
                worthy &= hasTriumph(playerid, recordHash)
        elif req == 'lowman':
            denies = sum([1 if 'denyTime' in key else 0 for key in roledata.keys()])
            timeParse = lambda i, spec: datetime.strptime(roledata[f'denyTime{i}'][spec], "%d/%m/%Y %H:%M")
            disallowed = [(timeParse(i, 'startTime'), timeParse(i, 'endTime')) for i in range(denies)]
            worthy &= hasLowman(playerid, 
                            roledata['playercount'], 
                            roledata['activityHashes'], 
                            flawless=roledata.get('flawless', False), 
                            disallowed=disallowed
                            )
        elif req == 'roles':
            return False #checked later
    return worthy



def returnIfHasRoles(playerid, role, year):
    if hasRole(playerid, role, year):
        return role
    return None

def getPlayerRoles(playerid, existingRoles = []):
    print(f'getting roles for {playerid}')
    roles = []
    redundantRoles = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        processes = []
        for year, yeardata in requirementHashes.items():		
            for role, roledata in yeardata.items():
                # if role in existingRoles or ('replaced_by' in roledata.keys() and any([x in existingRoles for x in roledata['replaced_by']])):
                #     if not 'Raid Master' in role:
                #         roles.append(role)
                #     continue
                # enable to not recheck existing roles
                processes.append(executor.submit(returnIfHasRoles, playerid, role, year))

    for task in as_completed(processes):
        if task.result():
            roles.append(task.result())

    #remove roles that are replaced by others
    for yeardata in requirementHashes.values():
        for role, roledata in yeardata.items():
            if role not in roles:
                redundantRoles.append(role)
            if 'replaced_by' in roledata.keys():
                for superior in roledata['replaced_by']:
                    if superior in roles and role in roles:
                        roles.remove(role)
                        redundantRoles.append(role)

    #check whether player is Yx Raid Master and add/remove roles
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
    return (roles, redundantRoles)

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
            await discordUser.remove_roles(roleObj)