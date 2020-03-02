from events.base_event      import BaseEvent

from functions import getUserIDbySnowflakeAndClanLookup, assignRolesToUser, removeRolesFromUser
from functions import isUserInClan, getPlayerRoles, getFullMemberMap, getUserMap

from dict import clanids

fullMemberMap = getFullMemberMap()


class AutomaticRoleAssignment(BaseEvent):
    """Will automatically update the roles"""

    def __init__(self):
        interval_minutes = 1440  # Set the interval for this event 1440 = 12h
        super().__init__(interval_minutes)

    async def run(self, client):
        #aquires the newtonslab channel from the descend server and notifies about starting
        newtonslab = client.get_channel(670637036641845258) 
        await newtonslab.send('running role update...')

        #Since I'm too lazy to find out the guild-id, this is how I get the guild-object
        guild = newtonslab.guild
        for discordUser in guild.members:
            #gets Users Destiny-ID from the DB
            destinyID = getUserMap(discordUser.id)
            if not destinyID:
                #or check the clan for similar names
                destinyID = getUserIDbySnowflakeAndClanLookup(discordUser,fullMemberMap)
                if destinyID:
                    await newtonslab.send(f'''Hi! User {discordUser.name} aka {discordUser.nick} was not found in my database!\nIf his rr is https://raid.report/pc/{pcid} please use ```!forceregister {discordUser.id} {pcid}```''')
                elif not discordUser.bot: #If the ID stil doesn't exist AND the user isn't a bot
                    await newtonslab.send(f'''Hi! User {discordUser.name} aka {discordUser.nick} was not found in my database!\nPlease use ```!forceregister {discordUser.id} <destinyID>``` so he can get synced next time''')
                    continue
            
            #gets the roles of the specific player and assigns/removes them
            (newRoles, removeRoles) = getPlayerRoles(destinyID, [role.name for role in discordUser.roles]) #the list of roles may be used to not check existing roles
            await assignRolesToUser(newRoles, discordUser, guild)
            await removeRolesFromUser(removeRoles, discordUser, guild)

            #Auto-Assigns Descend role if player is in the clan (or any other clan registered in dict.py)
            for clanid, rolename in clanids.items():
                if isUserInClan(destinyID,clanid):
                    await assignRolesToUser([rolename],discordUser,guild)
                else:
                    await removeRolesFromUser([rolename], discordUser, guild)
        await newtonslab.send('done with role update <:CaydeThumbsUp:670997683774685234>')
