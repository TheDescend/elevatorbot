
from commands.base_command import BaseCommand
import discord
from functions import getUserMap
import requests, config

class updateNames(BaseCommand):

    def __init__(self):
        description = "[dev] Updates all names [Admins role only]"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        PARAMS = {'X-API-Key':config.BUNGIE_TOKEN}
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer') 
        if admin not in message.author.roles and dev not in message.author.roles:
            return

        memberlist = sorted(message.guild.members, key=lambda x: x.id)
        ziplist = [(member, getUserMap(member.id)) for member in memberlist]
        

        for (discUser, destID) in ziplist:
            if destID is None:
                continue
            url = 'https://www.bungie.net/platform/User/GetMembershipsById/{}/{}/'.format(destID,3)
            r=requests.get(url=url, headers=PARAMS)
            memberships = r.json()['Response']['destinyMemberships']
            membership = None
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
                await discUser.edit(nick=newNick)
                print(f'set {discUser.id}:{discUser.name}\'s nickname to {newNick}')
                memberlist.remove(discUser)
            except discord.Forbidden as e:
                print(f'failed {newNick} -> {discUser.nick}: {e}')

        await message.channel.send(f'following people didn\'t have it linked and weren\'t updated:\n{", ".join([member.name for member in memberlist])} ')
        
        

