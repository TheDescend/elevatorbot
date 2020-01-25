
from commands.base_command import BaseCommand
import discord
from functions import getUserMap
import requests, config

class updateNames(BaseCommand):

    def __init__(self):
        description = "Updates all names [Admins role only]"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        PARAMS = {'X-API-Key':config.BUNGIE_TOKEN}
        roleObj = discord.utils.get(message.guild.roles, name='Admins') or discord.utils.get(message.guild.roles, name='Admin')
        if (not roleObj or roleObj not in message.author.roles) and message.author.id != 171650677607497730:
            await message.channel.send('You are not an Admin, sorry')
            return

        memberlist = sorted(message.guild.members, key=lambda x: x.id)
        ziplist = [(member,member.id) for member in memberlist]
        #mappedUsers = zip(memberlist, map(getUserMap, idlist))
        #print(mappedUsers)
        ziplist = [(member, getUserMap(memberid)) for (member, memberid) in ziplist]
        
        #print(ziplist)

        for (discUser, destID) in ziplist:
            #print(f'checking {discUser.name} with {destID}')
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
        
        

