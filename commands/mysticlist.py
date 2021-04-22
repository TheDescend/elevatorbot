import discord
from discord.ext import commands

from commands.base_command import BaseCommand
from functions.formating import embed_message
from functions.miscFunctions import hasMentionPermission

import json

def names(userdict, client):
    return ', '.join(map(lambda p:c.name if (c:=client.get_user(p['id'])) else 'user gone', userdict))

# has been slashified
#angessi,Neria,Lordopott,Meg,Stian,Tøm ♡
class mysticadd(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Add youself to mystics carry-list. Mystic and the admins can use pings to add other players"
        params = []
        topic = "Destiny"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        playerlist = []
        with open('database/mysticlist.json', 'r') as mlist:
            players = json.load(mlist)

        # check perm for other user mention, otherwise abort
        if not (await hasMentionPermission(message, mentioned_user, additional_users=[211838266834550785])): #mystic
            return

        players.append({'name': mentioned_user.name, 'id':mentioned_user.id})

        with open('commands/mysticlog.log', 'a') as mlog:
            mlog.write(f'\n{message.author.name} added {mentioned_user.name}')
        
        with open('database/mysticlist.json', 'w') as mlist:
            json.dump(players, mlist)
        await message.channel.send(f"Added {mentioned_user.name} to the mysticlist, it now has {names(players, client)}")

# has been slashified
class mysticremove(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Remove youself from mystics carry-list\nMystic and the admins can use pings to remove other players"
        params = []
        topic = "Destiny"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        # check perm for other user mention, otherwise abort
        if not (await hasMentionPermission(message, mentioned_user, additional_users=[211838266834550785])): #mystic
            return

        playerlist = []
        with open('database/mysticlist.json', 'r') as mlist:
            playerlist = json.load(mlist)
        
        if len(player := list(filter(lambda user:user['id']==mentioned_user.id, playerlist))) == 1:
            playerlist.remove(player[0])
            with open('commands/mysticlog.log', 'a') as mlog:
                mlog.write(f'\n{message.author.name} removed {mentioned_user.name}')
        
            with open('database/mysticlist.json', 'w+') as mlist:
                json.dump(playerlist, mlist)
            await message.channel.send(f"Removed {mentioned_user.name} from the mysticlist, it now has {names(playerlist, client)}")
            return
        
        await message.channel.send(f"User {mentioned_user.name} no found in the playerlist: \n{names(playerlist, client)}")

# has been slashified
class mystic(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Prints Mystics abandoned carry list. Tbf he said he tried ¯\_(ツ)_/¯"
        params = []
        topic = "Destiny"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        with open('database/mysticlist.json', 'r+') as mlist:
            playerlist = json.load(mlist)
            await message.channel.send(f"It has {names(playerlist, client)}")