from events.base_event      import BaseEvent
from commands.base_command  import BaseCommand
from utils                  import get_channel

from datetime               import datetime
from commands.getRoles      import getAllRoles

from functions import getUserIDbySnowflakeAndClanLookup, assignRolesToUser, removeRolesFromUser
from functions import isUserInClan, getPlayerRoles, getFullMemberMap

from dict import clanids

fullMemberMap = getFullMemberMap()
# Your friendly example event
# You can name this class as you like, but make sure to set BaseEvent
# as the parent class
class AutomaticRoleAssignment(BaseEvent):

    def __init__(self):
        interval_minutes = 1  # Set the interval for this event 1440 = 12h
        super().__init__(interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    async def run(self, client):
        print('running role analysis')
        #print(clanids)
        for guild in client.guilds:
            for discordUser in guild.members:
                destinyID = getUserIDbySnowflakeAndClanLookup(discordUser,fullMemberMap)
                if not destinyID:
                    print(f'failed for user {discordUser.name}')
                    continue
                (newRoles, removeRoles) = getPlayerRoles(destinyID)
                await assignRolesToUser(newRoles, discordUser, guild)
                await removeRolesFromUser(removeRoles, discordUser, guild)

                for clanid, rolename in clanids.items():
                    #print(f'checking clan {clanids[clanid]} for user {discordUser.name}')
                    if isUserInClan(destinyID,clanid):
                        #print(f'{discordUser.name} is in clan {clanids[clanid]}')
                        await assignRolesToUser([rolename],discordUser,guild)
                    else:
                        #print(f'{discordUser.name} is not in clan {clanids[clanid]}')
                        await removeRolesFromUser([rolename], discordUser, guild)
                    
        #channel = get_channel(client, "testing")
        #await channel.send('automatic role-assignment complete')
