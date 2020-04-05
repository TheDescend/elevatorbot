from events.base_event              import BaseEvent

from functions.roles                import assignRolesToUser, removeRolesFromUser, getPlayerRoles
from functions.dataTransformation   import getUserIDbySnowflakeAndClanLookup, getFullMemberMap, isUserInClan
from functions.database             import lookupDestinyID
from functions.dataLoading          import initDB

from static.dict import clanids

from itertools import compress

fullMemberMap = getFullMemberMap()


class AutomaticRoleAssignment(BaseEvent):
    """Will automatically update the roles"""

    def __init__(self):
        interval_minutes = 1440 # Set the interval for this event 1440 = 24h
        super().__init__(interval_minutes)

    async def run(self, client):
        #aquires the newtonslab channel from the descend server and notifies about starting
        newtonslab = client.get_channel(670637036641845258) 
        await newtonslab.send('running db update...')
        async with newtonslab.typing():
            initDB()
        await newtonslab.send('db done')
        await newtonslab.send('running role update...')

        unknownlist = []

        async with newtonslab.typing():
            #Since I'm too lazy to find out the guild-id, this is how I get the guild-object
            guild = newtonslab.guild
            for discordUser in guild.members:
                #gets Users Destiny-ID from the DB

                if discordUser.bot:
                    continue

                destinyID = lookupDestinyID(discordUser.id)
                if not destinyID and 'The Descend' in [r.name for r in discordUser.roles]:
                    #or check the clan for similar names
                    destinyID = getUserIDbySnowflakeAndClanLookup(discordUser,fullMemberMap)
                    if not destinyID:
                        unknownlist.append(discordUser.name)
                        continue
                    await newtonslab.send(f'Auto-Matched {discordUser.name} with {destinyID} \n check https://raid.report/pc/{destinyID}\n if that is correct, do ```!forceregister {discordUser.id} {destinyID}```' )

                #gets the roles of the specific player and assigns/removes them
                (newRoles, removeRoles) = getPlayerRoles(destinyID, [role.name for role in discordUser.roles]) #the list of roles may be used to not check existing roles
                assign = await assignRolesToUser(newRoles, discordUser, guild)
                remove = await removeRolesFromUser(removeRoles, discordUser, guild)

                if not assign:
                    await newtonslab.send(f'Assigning roles {", ".join(newRoles)} failed for {discordUser.name}')
                if not remove:
                    await newtonslab.send(f'Removing roles {", ".join(removeRoles)} failed for {discordUser.name}')

                #Auto-Assigns Descend role if player is in the clan (or any other clan registered in dict.py)
                # for clanid, rolename in clanids.items():
                #     if isUserInClan(destinyID,clanid):
                #         await assignRolesToUser([rolename],discordUser,guild)
                #     else:
                #         await removeRolesFromUser([rolename], discordUser, guild)
                existingRoles = [er.name for er in discordUser.roles]
                addBools = [nr not in existingRoles for nr in newRoles]
                removeBools = [rr in existingRoles for rr in removeRoles]

                addrls = list(compress(newRoles, addBools))
                removerls = list(compress(removeRoles, removeBools))
                if any(addBools) or any(removeBools):
                    await newtonslab.send(f'updated player {discordUser.name} by removing {", ".join(removerls or ["nothing"])} and adding {", ".join(addrls or ["nothing"])}')
            
        await newtonslab.send(f"didn't find profiles for {', '.join(unknownlist)}")
        await newtonslab.send('done with role update <:CaydeThumbsUp:670997683774685234>')
