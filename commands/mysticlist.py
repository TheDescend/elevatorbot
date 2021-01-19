import discord
from discord.ext import commands

from commands.base_command import BaseCommand
from functions.formating import embed_message
from functions.miscFunctions import hasMentionPermission


class mysticadd(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Add youself to mystics carry-list\nMystic and the admins can use pings to add other players"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        playerlist = []
        with open('commands/mysticlist.list', 'r') as mlist:
            playerlist = mlist.read().split(',')

        # check perm for other user mention, otherwise abort
        if not (await hasMentionPermission(message, mentioned_user)):
            return

        playerlist.append(f'{mentioned_user.name}')

        with open('commands/mysticlog.log', 'a') as mlog:
            mlog.write(f'\n{message.author.name} added {mentioned_user.name}')
        
        with open('commands/mysticlist.list', 'w') as mlist:
            mlist.write(",".join(playerlist))
        await message.channel.send(f"Added {mentioned_user.name} to the mysticlist, it now has {', '.join(playerlist)}")


class mysticremove(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Remove youself from mystics carry-list\nMystic and the admins can use pings to remove other players"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        # check perm for other user mention, otherwise abort
        if not (await hasMentionPermission(message, mentioned_user)):
            return

        playerlist = []
        with open('commands/mysticlist.list', 'r') as mlist:
            playerlist = mlist.read().split(',')
        
        for name in playerlist[:]:
            if mentioned_user.name.lower() == name.lower():
                playerlist.remove(name)
                await message.channel.send(f"Removed {mentioned_user.name} from the mysticlist, it now has {', '.join(playerlist)}")
                with open('commands/mysticlog.log', 'a') as mlog:
                    mlog.write(f'\n{message.author.name} removed {mentioned_user.name}')
        
                with open('commands/mysticlist.list', 'w+') as mlist:
                    mlist.write(",".join(playerlist))
                return
        
        await message.channel.send(f"User {mentioned_user.name} no found in the playerlist: \n{', '.join(playerlist)}")


class mystic(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Whom to carry"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        with open('commands/mysticlist.list', 'r+') as mlist:
            playerlist = mlist.read().split(',')
            await message.channel.send(f"It has {', '.join(playerlist)}")