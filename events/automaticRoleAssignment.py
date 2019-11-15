from events.base_event      import BaseEvent
from commands.base_command  import BaseCommand
from utils                  import get_channel

from datetime               import datetime
from commands.getRoles      import getAllRoles

from functions import getUserIDbySnowflakeAndClanLookup, assignRolesToUser, removeRolesFromUser, getPlayerRoles, getFullMemberMap
fullMemberMap = getFullMemberMap()
# Your friendly example event
# You can name this class as you like, but make sure to set BaseEvent
# as the parent class
class AutomaticRoleAssignment(BaseEvent):

    def __init__(self):
        interval_minutes = 1440  # Set the interval for this event 1440 = 12h
        super().__init__(interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    async def run(self, client):
        for guild in client.guilds:
            for discordUser in guild.members:
                destinyID = getUserIDbySnowflakeAndClanLookup(discordUser,fullMemberMap)
                if not destinyID:
                    print(f'failed for user {discordUser.name}')
                    continue
                (newRoles, removeRoles) = getPlayerRoles(destinyID)
                await assignRolesToUser(newRoles, discordUser, guild)
                await removeRolesFromUser(removeRoles, discordUser, guild)
        #channel = get_channel(client, "testing")
        #await channel.send('automatic role-assignment complete')
