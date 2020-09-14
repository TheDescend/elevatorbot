
from commands.base_command import BaseCommand
import discord
from functions.database import lookupDestinyID
from functions.roles import hasAdminOrDevPermissions
from static.config      import BUNGIE_TOKEN
import requests

class updateNames(BaseCommand):

    def __init__(self):
        description = "[dev] Updates all names [Admins role only]"
        params = None
        topic = "Registration"
        super().__init__(description, params, topic)

    async def handle(self, params, message, client):
        PARAMS = {'X-API-Key':BUNGIE_TOKEN}

        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        memberlist = sorted(message.guild.members, key=lambda x: x.id)
        ziplist = [(member, lookupDestinyID(member.id)) for member in memberlist]
        

        for (discUser, destID) in ziplist:
            if destID is None:
                continue
            url = 'https://www.bungie.net/platform/User/GetMembershipsById/{}/{}/'.format(destID,3)
            r=requests.get(url=url, headers=PARAMS)
            memberships = r.json()['Response']['destinyMemberships']
            
            if memberships[0]['crossSaveOverride'] and memberships[0]['crossSaveOverride'] != memberships[0]['membershipType']:
                newtype = memberships[0]['crossSaveOverride']
                for memship in memberships:
                    print(memship)
                    if memship['membershipType'] == newtype:
                        print(f'found other type for {discUser.name}')
                        membership = memship
                        break
            else:
                membership = memberships[0]
            if not membership:
                print(f'failed for {discUser.name}')
                continue
            newNick = membership['LastSeenDisplayName']
            try:
                #await discUser.edit(nick=newNick)
                print(f'set {discUser.id}:{discUser.name}\'s nickname to {newNick}')
                memberlist.remove(discUser)
            except discord.Forbidden as e:
                print(f'failed {newNick} -> {discUser.nick}: {e}')

        await message.channel.send(f'following people didn\'t have it linked and weren\'t updated:\n{", ".join([member.name for member in memberlist])} ')
        
        

