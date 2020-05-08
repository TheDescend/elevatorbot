from commands.base_command  import BaseCommand

from functions.dataLoading        import getNameAndCrossaveNameToHashMapByClanid
from static.dict                  import clanids
from functions.database           import lookupDiscordID

class getUserMatching(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] match ingame and Discord names"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        
        for clanid,name in clanids.items():
            await message.channel.send(f'matching members for clan {name}')
            clanmap = getNameAndCrossaveNameToHashMapByClanid(clanid)
            successfulMatches = []
            unsuccessfulMatches = []
            for userid, (steamname, crosssavename) in clanmap.items():
                discordID = lookupDiscordID(userid)
                if discordID:
                    # user could be matched
                    user = client.get_user(discordID)
                    if user:
                        successfulMatches.append((steamname, crosssavename, user.name))
                    else:
                        await message.channel.send(f'[ERROR] {username} with destinyID {userid} has discordID {discordID} but it is faulty')
                else:
                    # user not found
                    unsuccessfulMatches.append((steamname, crosssavename, userid))

            await message.channel.send('SUCCESSFUL MATCHES:')
            sortedSuccessfulMatches = sorted(successfulMatches, key=lambda pair: pair[2].lower())
            for (steamname, crosssavename, username) in sortedSuccessfulMatches:  
                await message.channel.send(f'{username} has successfully been matched to {steamname} / {crosssavename}')

            await message.channel.send('FAILED MATCHES:')
            unsuccessfulMessage = ''
            for (steamname, crosssavename, userid) in unsuccessfulMatches:    
                unsuccessfulMessage += f'{steamname} / {crosssavename} (Steam-ID {userid}) could not be found in Discord \n'  
            await message.channel.send(unsuccessfulMessage)      