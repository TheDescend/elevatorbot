
from commands.base_command import BaseCommand
import discord
from functions import getMultipleUserMap
import requests, config

class updateNames(BaseCommand):

    def __init__(self):
        description = "Updates all names [Admins role only]"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        PARAMS = {'X-API-Key':config.BUNGIE_TOKEN}
        roleObj = discord.utils.get(message.guild.roles, name='Admins') or discord.utils.get(message.guild.roles, name='Admin')
        if not roleObj or roleObj not in message.author.roles:
            await message.channel.send('You are not an Admin, sorry')
            return

        memberlist = message.guild.members
        memberidlist = [member.id for member in memberlist]
        mappedUsers = getMultipleUserMap(memberidlist)


        for (discID, destID) in mappedUsers:
            discUser = message.guild.get_member(discID)
            url = 'https://www.bungie.net/platform/User/GetMembershipsById/{}/{}/'.format(destID,3)
            r=requests.get(url=url, headers=PARAMS)
            membership = r.json()['Response']['destinyMemberships'][0]
            newNick = membership['LastSeenDisplayName']
            await discUser.edit(nick=newNick)
            print(f'set {discUser.name}\'s nickname to {newNick}')
            memberlist.remove(discUser)
        await message.channel.send(f'following people didn\'t have it linked and weren\'t updated:\n{" ,".join([member.name for member in memberlist])} ')
        
        

