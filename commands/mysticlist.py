import discord
from discord.ext import commands

from commands.base_command import BaseCommand
from functions.formating import embed_message


class mysticadd(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Add youself to mystics carry-list\nMystic and the admins can use pings to add other players"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        playerlist = []
        with open('commands/mysticlist.list', 'r') as mlist:
            playerlist = mlist.read().split(',')

        if len(params) == 1:
            #admin only

            admin = discord.utils.get(message.guild.roles, name='Admin')
            dev = discord.utils.get(message.guild.roles, name='Developer')
            if admin not in message.author.roles and dev not in message.author.roles and not message.author.id == 211838266834550785:
                await message.channel.send(embed=embed_message(
                    'Error',
                    'You are not allowed to do that, ask a mod or Mystic himself\n Otherwise use no argument to add yourself'
                ))
                return

            ctx = await client.get_context(message)
            try:
                user = await commands.MemberConverter().convert(ctx, params[0])
            except:
                await message.channel.send(embed=embed_message(
                    'Error',
                    f'User not valid, make sure the spelling/id is correct'
                ))
                return
        else:
            user = message.author

        playerlist.append(f'{user.name}')

        with open('commands/mysticlog.log', 'a') as mlog:
            mlog.write(f'\n{message.author.name} added {user.name}')
        
        with open('commands/mysticlist.list', 'w') as mlist:
            mlist.write(",".join(playerlist))
        await message.channel.send(f"Added {user.name} to the mysticlist, it now has {', '.join(playerlist)}")

class mysticremove(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Remove youself from mystics carry-list\nMystic and the admins can use pings to remove other players"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        if len(params) == 1:
            #admin only

            admin = discord.utils.get(message.guild.roles, name='Admin')
            dev = discord.utils.get(message.guild.roles, name='Developer')
            if admin not in message.author.roles and dev not in message.author.roles and not message.author.id == 211838266834550785:
                await message.channel.send(embed=embed_message(
                    'Error',
                    'You are not allowed to do that, ask a mod or Mystic himself\n Otherwise use no argument to remove yourself'
                ))
                return

            ctx = await client.get_context(message)
            try:
                user = await commands.MemberConverter().convert(ctx, params[0])
            except:
                await message.channel.send(embed=embed_message(
                    'Error',
                    f'User not valid, make sure the spelling/id is correct'
                ))
                return
        else:
            user = message.author

        playerlist = []
        with open('commands/mysticlist.list', 'r') as mlist:
            playerlist = mlist.read().split(',')
        
        for name in playerlist[:]:
            if user.name.lower() == name.lower():
                playerlist.remove(name)
                await message.channel.send(f"Removed {user.name} from the mysticlist, it now has {', '.join(playerlist)}")
                with open('commands/mysticlog.log', 'a') as mlog:
                    mlog.write(f'\n{message.author.name} removed {user.name}')
        
                with open('commands/mysticlist.list', 'w+') as mlist:
                    mlist.write(",".join(playerlist))
                return
        
        await message.channel.send(f"User {user.name} no found in the playerlist: \n{', '.join(playerlist)}")

class mystic(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Whom to carry"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        with open('commands/mysticlist.list', 'r+') as mlist:
            playerlist = mlist.read().split(',')
            await message.channel.send(f"It has {', '.join(playerlist)}")