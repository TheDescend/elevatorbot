from events.base_event      import BaseEvent

from functions import getUserIDbySnowflakeAndClanLookup, assignRolesToUser, removeRolesFromUser
from functions import isUserInClan, getPlayerRoles, getFullMemberMap, getUserMap

from dict import clanids

fullMemberMap = getFullMemberMap()

class AutomaticRoleAssignment(BaseEvent):

    def __init__(self):
        interval_minutes = 1440  # Set the interval for this event 1440 = 12h
        super().__init__(interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    async def run(self, client):
        print('running role analysis')
        for guild in client.guilds:
            for discordUser in guild.members:

                destinyID = getUserMap(discordUser.id)
                if not destinyID:
                    destinyID = getUserIDbySnowflakeAndClanLookup(discordUser,fullMemberMap)

                if not destinyID:
                    print(f'failed for user {discordUser.name}')
                    continue
                (newRoles, removeRoles) = getPlayerRoles(destinyID)
                await assignRolesToUser(newRoles, discordUser, guild)
                await removeRolesFromUser(removeRoles, discordUser, guild)

                for clanid, rolename in clanids.items():
                    if isUserInClan(destinyID,clanid):
                        await assignRolesToUser([rolename],discordUser,guild)
                    else:
                        await removeRolesFromUser([rolename], discordUser, guild)
