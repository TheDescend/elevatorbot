from functions.dataTransformation   import hasFlawless, hasCollectible, hasTriumph
from functions.dataTransformation   import getPlayerCount, getPlayersPastPVE, getClearCount, hasLowman
from functions.network  import getJSONfromURL
from functions.formating import embed_message

from static.dict                    import requirementHashes

from datetime           import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import discord


# check if user has permission to use this command
async def hasAdminOrDevPermissions(message, send_message=True):
    admin = discord.utils.get(message.guild.roles, name='Admin')
    dev = discord.utils.get(message.guild.roles, name='Developer')
    if admin not in message.author.roles and dev not in message.author.roles:
        if send_message:
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to do that'
            ))
        return False
    return True


def hasRole(playerid, role, year, br = True):
    data = {}

    roledata = requirementHashes[year][role]
    if not 'requirements' in roledata:
        print('malformatted requirementHashes')
        return [False, data]
    worthy = True

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
            has_fla = hasFlawless(playerid, roledata['flawless'])
            worthy &= has_fla

            data["Flawless"] = str(has_fla)

        elif req == 'collectibles':
            for collectible in roledata['collectibles']:
                has_col = hasCollectible(playerid, collectible)
                worthy &= has_col

                if (not worthy) and br:
                    break

                # get name of collectible
                name = "No name here"
                rep = getJSONfromURL(f"https://www.bungie.net/Platform/Destiny2/Manifest/DestinyCollectibleDefinition/{collectible}/")
                if rep and rep['Response']:
                    name = rep['Response']["displayProperties"]["name"]
                data[str(name)] = str(has_col)

        elif req == 'records':
            for recordHash in roledata['records']:
                has_tri = hasTriumph(playerid, recordHash)
                worthy &= has_tri

                if (not worthy) and br:
                    break

                # get name of triumph
                name = "No name here"
                rep = getJSONfromURL(
                    f"https://www.bungie.net/Platform/Destiny2/Manifest/DestinyRecordDefinition/{recordHash}/")
                if rep and rep['Response']:
                    name = rep['Response']["displayProperties"]["name"]
                data[str(name)] = str(has_tri)

        elif req == 'lowman':
            denies = sum([1 if 'denyTime' in key else 0 for key in roledata.keys()])
            timeParse = lambda i, spec: datetime.strptime(roledata[f'denyTime{i}'][spec], "%d/%m/%Y %H:%M")
            disallowed = [(timeParse(i, 'startTime'), timeParse(i, 'endTime')) for i in range(denies)]
            has_low = hasLowman(playerid,
                            roledata['playercount'], 
                            roledata['activityHashes'], 
                            flawless=roledata.get('flawless', False), 
                            disallowed=disallowed
                            )
            worthy &= has_low

            data["Lowman (" + str(roledata['playercount']) + " Players)"] = str(has_low)

        elif req == 'roles':
            return [False, data] #checked later

        if (not worthy) and br:
            break

    # print(data)
    return [worthy, data]

def returnIfHasRoles(playerid, role, year):
    if hasRole(playerid, role, year)[0]:
        return role
    return None

def getPlayerRoles(playerid, existingRoles = []):
    if not playerid:
        print('got empty playerid')
        return ([],[])
    print(f'getting roles for {playerid}')
    roles = []
    redundantRoles = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        processes = []
        for year, yeardata in requirementHashes.items():		
            for role, roledata in yeardata.items():
                if role in existingRoles or ('replaced_by' in roledata.keys() and any([x in existingRoles for x in roledata['replaced_by']])):
                    if not 'Raid Master' in role:
                        roles.append(role)
                    continue
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
                    #print('worthy for ', role)
                    roles.append(role)
                    redundantRoles.remove(role)
                    for reqrole in reqs:
                        roles.remove(reqrole)
                        redundantRoles.append(reqrole)
    return (roles, redundantRoles)

async def assignRolesToUser(roleList, discordUser, guild):
    #takes rolelist as string array, userSnowflake, guild object
    if not discordUser:
        return False
    for role in roleList:
        #print(guild.roles)
        roleObj = discord.utils.get(guild.roles, name=role) or discord.utils.get(guild.roles, id=role)
        if not roleObj:
            if guild.id not in [556418279015448596, 724676552175910934, 540482071571857408]: #Crashtest dummy, emote server, kinderguardian
                print(f'assignable role doesn\'t exist in {guild.name} with id {guild.id}: {role}')
            continue
        if roleObj not in discordUser.roles:
            print(f'added role {roleObj.name} to user {discordUser.name}')
            try:
                await discordUser.add_roles(roleObj)
            except discord.errors.Forbidden:
                return False
    return True

async def removeRolesFromUser(roleStringList, discordUser, guild):
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
                await discordUser.remove_roles(roleObj)
            except discord.errors.Forbidden:
                return False
    return True