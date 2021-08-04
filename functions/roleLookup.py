from datetime import datetime
from typing import Optional, Union

import discord
import asyncio
import time

from database.database import getFlawlessHashes, getClearCount, getDestinyDefinition
from functions.dataTransformation import hasLowman
from functions.dataTransformation import hasCollectible, hasTriumph
from static.dict import requirementHashes, requirement_hashes_without_years
# check if user has permission to use this command
from static.globals import role_ban_id, divider_legacy_role_id



async def has_role(destiny_id: int, role: discord.Role, return_as_bool: bool = True) -> Optional[list[Union[bool, dict]]]:
    """ return_as_bool may be set to True if only True/False is expected, set to False to get complete data on why or why not the user earned the role """
    data = {}

    try:
        roledata = requirement_hashes_without_years[role.name]
    except KeyError:
        # This role cannot be earned through destiny
        return None

    worthy = True
    start_reqs = time.monotonic()
    for req in roledata['requirements']:
        if req == 'clears':
            creq = roledata['clears']
            i = 1
            for raid in creq:
                actualclears = await getClearCount(destiny_id, raid['actHashes'])
                if not actualclears >= raid['count']:
                    worthy = False

                data["Clears #" + str(i)] = str(actualclears) + " / " + str(raid['count'])
                i += 1

        elif req == 'flawless':
            has_fla = bool(await getFlawlessHashes(destiny_id, roledata['flawless']))
            worthy &= has_fla

            data["Flawless"] = bool(has_fla)

        elif req == 'collectibles':
            for collectibleHash in roledata['collectibles']:
                has_coll_start = time.monotonic()
                has_col = await hasCollectible(destiny_id, collectibleHash)
                has_coll_end = time.monotonic()
                if (diff := has_coll_end - has_coll_start) > 1:
                    print(f'hasCollectible took {diff} seconds')
                worthy &= has_col

                if (not worthy) and return_as_bool:
                    break
                
                if not return_as_bool:
                    # get name of collectible
                    # str conversion required because dictionary is indexed on strings, not postiions
                    coll_def_start = time.monotonic()
                    (_, _, name, *_) = await getDestinyDefinition("DestinyCollectibleDefinition", collectibleHash)
                    coll_def_end = time.monotonic()
                    if (diff := coll_def_end - coll_def_start) > 1:
                        print(f'getDestinyDefinition in collectibles took {diff} seconds')
                    data[name] = bool(has_col)

        elif req == 'records':
            for recordHash in roledata['records']:
                has_tri = await hasTriumph(destiny_id, recordHash)
                worthy &= has_tri

                if (not worthy) and return_as_bool:
                    break
                
                if not return_as_bool:
                    # get name of triumph
                    (_, _, name, *_) = await getDestinyDefinition("DestinyRecordDefinition", recordHash)
                    data[name] = bool(has_tri)

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
                destiny_id,
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
                required_role_discord = discord.utils.get(role.guild.roles, name=required_role)
                if not required_role_discord:
                    req_worthy = False
                    req_data = {}
                else:
                    req_worthy, req_data = await has_role(destiny_id, required_role_discord)

                # only worthy if worthy for all required roles
                worthy &= req_worthy

                # merging dicts, data dominates
                data = {**req_data, **data}
                data[f'Role: {required_role}'] = bool(req_worthy)

        if (not worthy) and return_as_bool:
            break
    end_reqs = time.monotonic() - start_reqs
    if end_reqs > 1:
        print(f'took {end_reqs} seconds to check requirements for {role}')
    return [worthy, data]


async def get_player_roles(guild: discord.Guild, destiny_id: int, role_names_to_ignore: list[str] = None) -> tuple[list[discord.Role], list[discord.Role]]:
    """ Returns destiny achievement roles for the player """

    # get all roles from the dict to check them later. asyncio.gather keeps order
    roles_to_check = [
        role
        for year, yeardata in requirementHashes.items()
        for role in yeardata.keys()
        # if not role in roles
    ]

    # do not recheck existing roles or roles that will be replaced by existing roles
    if role_names_to_ignore:
        for year, yeardata in requirementHashes.items():
            for role, roledata in yeardata.items():
                if role in role_names_to_ignore or ('replaced_by' in roledata.keys() and any([x in role_names_to_ignore for x in roledata['replaced_by']])):
                    roles_to_check.remove(role)

    # ignore those, who don't exist in the specified discord guild and convert the strings to the actual discord roles.
    discord_roles_to_check = []
    for role in roles_to_check:
        discord_role = discord.utils.get(guild.roles, name=role)
        if discord_role:
            discord_roles_to_check.append(discord_role)

    # check worthiness in parallel
    starttime = time.time()
    result = await asyncio.gather(*[
        has_role(destiny_id, role)
        for role in discord_roles_to_check
    ])

    endtime = time.time() - starttime
    print(f'Took {endtime} seconds to gather has_oles for destinyID {destiny_id}')

    earned_discord_roles = [discord_role for (discord_role, (isworthy, worthydetails)) in zip(discord_roles_to_check, result) if isworthy]
    earned_roles = [discord_role.name for discord_role in earned_discord_roles]

    # remove roles that are replaced by others
    redundant_roles = []
    for yeardata in requirementHashes.values():
        for roleName, roledata in yeardata.items():
            if roleName not in earned_roles:
                redundant_roles.append(roleName)
            if 'replaced_by' in roledata.keys():
                for superior in roledata['replaced_by']:
                    if superior in earned_roles:
                        if roleName in earned_roles:
                            earned_discord_roles.pop(earned_roles.index(roleName))
                            earned_roles.remove(roleName)
                            redundant_roles.append(roleName)

            # give the user the divider role if they have a legacy role
            if ("deprecated" in roledata.keys()) and (divider_legacy_role_id not in earned_roles):
                earned_roles.append(divider_legacy_role_id)
                divider_role = guild.get_role(divider_legacy_role_id)
                if divider_role:
                    earned_discord_roles.append(divider_role)

    # ignore those, who don't exist in the specified discord guild and convert the strings to the actual discord roles.
    redundant_discord_roles = []
    for role in redundant_roles:
        discord_role = discord.utils.get(guild.roles, name=role)
        if discord_role:
            redundant_discord_roles.append(discord_role)

    return earned_discord_roles, redundant_discord_roles


async def assignRolesToUser(roleList, discordUser, guild, reason=None):
    # takes rolelist as string array, userSnowflake, guild object
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




