from commands.base_command  import BaseCommand
import os
from config import BUNGIE_OAUTH
from functions import getUserMap
from database import insertUser, removeUser, lookupUser
import discord

class registerDesc(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[depracted] register with bungie.net"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        state = str(message.author.id) + ':' + str(message.guild.id)
        URL = f'https://www.bungie.net/en/oauth/authorize?client_id={BUNGIE_OAUTH}&response_type=code&state={state}'
        await message.author.send(f'Open this link, to register with the bot: {URL}')
        await message.channel.send(f'sent dm to {message.author.nick or message.author.name}')

class getID(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] check a user's destinyID"
        params = ['User']
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        user = int(params[0])
        discordUser = client.get_user(user)
        if not discordUser:
             await message.channel.send(f'Unknown User {user}')
        await message.channel.send(f'{discordUser.name} has destinyID {lookupUser(user)}')


class checkregister(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] function to check your destinyID"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        await message.channel.send(f'User {message.author.nick or message.author.name} has ID {getUserMap(message.author.id)}')

class forceregister(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] function to create Discord-Destiny mappings"
        params = ['discordID', 'destinyID']
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer') 
        destinyID = params[0]
        if admin not in message.author.roles and dev not in message.author.roles and not message.author.id == params[0]:
            return
        oldid = lookupUser(destinyID)
        if oldid:
            await message.channel.send(f'User already registered with id {oldid}, use !unregister {params[0]} to undo that binding')
            return
        insertUser(destinyID, params[1], message.guild.id)
        await message.channel.send(f'inserted {params[0]}:{params[1]}')


class unregister(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] function to delete Users from the database"
        params = ['discordID']
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer') 
        if admin not in message.author.roles and dev not in message.author.roles and not message.author.id == params[0]:
            return
        if removeUser(params[0]):
            await message.author.send(f'removed {params[0]}')
        else:
            await message.author.send('removal failed for ', params[0])
        
