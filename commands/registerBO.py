from commands.base_command  import BaseCommand
import os
from config import BUNGIE_OAUTH
from functions import getUserMap
from database import insertUser

class registerBO(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "register with BOB"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        state = str(message.author.id) + ':' + str(message.guild.id)
        URL = f'https://www.bungie.net/en/oauth/authorize?client_id={BUNGIE_OAUTH}&response_type=code&state={state}'
        await message.author.send(f'Open this link, to register with the bot: {URL}')
        await message.channel.send(f'sent dm to {message.author.nick or message.author.name}')


class checkregister(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "dev function to check register"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        await message.channel.send(f'User {message.author.nick or message.author.name} has ID {getUserMap(message.author.id)}')

class forceregister(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "dev function to insert to db"
        params = ['dicordID', 'destinyID']
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        if message.author.id == 171650677607497730:
            insertUser(params[0], params[1], message.guild.id)
            print('inserted ', params[0],':', params[1])
        
