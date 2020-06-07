from events.base_event              import BaseEvent

from functions.roles                import assignRolesToUser, removeRolesFromUser, getPlayerRoles
from functions.dataTransformation   import getUserIDbySnowflakeAndClanLookup, getFullMemberMap, isUserInClan
from functions.database             import lookupDestinyID
from functions.dataLoading          import initDB

from static.dict import clanids

from multiprocessing import Process
from multiprocessing import Pool, TimeoutError

import concurrent.futures as cf

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

        def updateUser(discordUser):
            if discordUser.bot:
                return (None, None, None, None)

            destinyID = lookupDestinyID(discordUser.id)
            if not destinyID and 'The Descend' in [r.name for r in discordUser.roles]:
                #or check the clan for similar names
                destinyID = getUserIDbySnowflakeAndClanLookup(discordUser,fullMemberMap)
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
                newslist = []
                
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
                        newstext = f'Updated player {discordUser.name} by adding {", ".join(addrls or ["nothing"])} and removing {", ".join(removerls or ["nothing"])}'
                        await newtonslab.send('done with role update <:CaydeThumbsUp:670997683774685234>\n' + newstext)
        
        #await newtonslab.send('done with daily update <:CaydeThumbsUp:670997683774685234>')