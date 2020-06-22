from events.base_event              import BaseEvent

from functions.roles                import assignRolesToUser, removeRolesFromUser, getPlayerRoles
from functions.dataTransformation   import getFullMemberMap, isUserInClan
from functions.database             import lookupDestinyID, getToken
from functions.dataLoading          import initDB

from static.dict import clanids

from multiprocessing import Process
from multiprocessing import Pool, TimeoutError

import concurrent.futures as cf
import discord

from itertools import compress

fullMemberMap = getFullMemberMap()


class AutomaticRoleAssignment(BaseEvent):
    """Will automatically update the roles"""

    def __init__(self):
        interval_minutes = 1440 # Set the interval for this event 1440 = 24h
        super().__init__(interval_minutes)

        # if not assign:
        #     await newtonslab.send(f'Assigning roles {", ".join(newRoles)} failed for {discordUser.name}')
        # if not remove:
        #     await newtonslab.send(f'Removing roles {", ".join(removeRoles)} failed for {discordUser.name}')

        #Auto-Assigns Descend role if player is in the clan (or any other clan registered in dict.py)
        # for clanid, rolename in clanids.items():
        #     if isUserInClan(destinyID,clanid):
        #         await assignRolesToUser([rolename],discordUser,guild)
        #     else:
        #         await removeRolesFromUser([rolename], discordUser, guild)
        # existingRoles = [er.name for er in discordUser.roles]
        # addBools = [nr not in existingRoles for nr in newRoles]
        # removeBools = [rr in existingRoles for rr in removeRoles]

        # addrls = list(compress(newRoles, addBools))
        # removerls = list(compress(removeRoles, removeBools))
        # return [(discordUser.name, removerls or ["nothing"], addrls or ["nothing"])]
    
    async def run(self, client):
        print('running the automatic role assignment...')
        def updateUser(discordUser):
            if discordUser.bot:
                return (None, None, None, None)

            destinyID = lookupDestinyID(discordUser.id)
            if not destinyID:
                return (None, None, None, None)
                #await newtonslab.send(f'Auto-Matched {discordUser.name} with {destinyID} \n check https://raid.report/pc/{destinyID}' )

            #gets the roles of the specific player and assigns/removes them
            (newRoles, removeRoles) = getPlayerRoles(destinyID, [role.name for role in discordUser.roles]) #the list of roles may be used to not check existing roles
            

            return (guild, discordUser, newRoles, removeRoles)
        
        #aquires the newtonslab channel from the descend server and notifies about starting
        newtonslab = client.get_channel(670637036641845258)
        #await newtonslab.send('running db update...')
        async with newtonslab.typing():
            initDB()
        #await newtonslab.send('db done')
        #await newtonslab.send('running role update...')

        async with newtonslab.typing():
            #Since I'm too lazy to find out the guild-id, this is how I get the guild-object
            guild = newtonslab.guild
            with cf.ThreadPoolExecutor(max_workers=15) as executor:
                results = executor.map(updateUser, guild.members)

                news = list(results)
                newstext = 'done with role update <:CaydeThumbsUp:670997683774685234>\n'
                
                for guild, discordUser, newRoles,removeRoles in news:
                    if not discordUser:
                        continue
                    await assignRolesToUser(newRoles, discordUser, guild)
                    await removeRolesFromUser(removeRoles, discordUser, guild)
                    
                    existingRoles = [er.name for er in discordUser.roles]
                    addBools = [nr not in existingRoles for nr in newRoles]
                    removeBools = [rr in existingRoles for rr in removeRoles]

                    addrls = list(compress(newRoles, addBools))
                    removerls = list(compress(removeRoles, removeBools))
                    
                    if addrls or removerls:
                        newstext += f'Updated player {discordUser.name} by adding {", ".join(addrls or ["nothing"])} and removing {", ".join(removerls or ["nothing"])}\n'
                        
                await newtonslab.send(newstext)
        
        #await newtonslab.send('done with daily update <:CaydeThumbsUp:670997683774685234>')


raiderText = '⁣           Raider       ⁣'
raiderId = 670385313994113025
achText = '⁣        Achievements       ⁣'
achId = 670385837044662285
miscText = '⁣           Misc       ⁣  ⁣  ⁣'
miscId = 670395920327639085
class AutoRegisteredRole(BaseEvent):
    """Will automatically update the registration and the guest role"""
    def __init__(self):
        interval_minutes = 30  # Set the interval for this event 1440 = 24h
        super().__init__(interval_minutes)

    async def run(self, client):
        for guild in client.guilds:
            for member in guild.members:
                # dont do that for bots
                if not member.bot:
                    # add "Registered" if they have a token but not the role
                    if getToken(member.id):
                        if discord.utils.get(guild.roles, name="Not Registered") in member.roles:
                            await removeRolesFromUser(["Not Registered"], member, guild)
                            await assignRolesToUser(["Registered"], member, guild)
                    # add "Not Registered" if they have no token but the role (after unregister)
                    else:
                        if discord.utils.get(guild.roles, name="Registered") in member.roles:
                            await removeRolesFromUser(["Registered"], member, guild)
                            await assignRolesToUser(["Not Registered"], member, guild)

                    # add @guest if the clan role doesn't exist
                    if discord.utils.get(guild.roles, name="The Descend") not in member.roles:
                        await assignRolesToUser(["Guest"], member, guild)
                    # remove @guest if in clan
                    if discord.utils.get(guild.roles, name="The Descend") in member.roles:
                        await removeRolesFromUser(["Guest"], member, guild)

                    # add filler roles to everyone
                    if discord.utils.get(guild.roles, id=raiderId) not in member.roles:
                        await assignRolesToUser([raiderId], member, guild)
                    if discord.utils.get(guild.roles, id=achId) not in member.roles:
                        await assignRolesToUser([achId], member, guild)
                    if discord.utils.get(guild.roles, id=miscId) not in member.roles:
                        await assignRolesToUser([miscId], member, guild)
