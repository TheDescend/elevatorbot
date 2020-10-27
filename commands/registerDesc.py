from commands.base_command  import BaseCommand
import os
from static.config import BUNGIE_OAUTH
from functions.database import removeUser, lookupDestinyID, lookupDiscordID
from functions.formating import embed_message
from functions.roles import hasAdminOrDevPermissions
from events.automaticRoleAssignment import AutoRegisteredRole

import discord

class register(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Register with bungie.net"
        params = []
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        await elevatorRegistration(message)


class registerDesc(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Shadows !register, but don't get picked up from Charlemange"
        params = []
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        await elevatorRegistration(message)


async def elevatorRegistration(message):
    if not message.guild:
        await message.author.send('Please use this command in your clans bot-channel')
        return
    state = str(message.author.id) + ':' + str(message.guild.id)
    URL = f'https://www.bungie.net/en/oauth/authorize?client_id={BUNGIE_OAUTH}&response_type=code&state={state}'
    await message.author.send(embed=embed_message(
        f'Registration',
        f'[Click here to register with the bot]({URL})'
    ))
    await message.channel.send(embed=embed_message(
        'Registration',
        f'Sent a DM to {message.author.nick or message.author.name}'
    ))


class checkregister(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] function to check your destinyID"
        params = []
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        await message.channel.send(f'User {message.author.nick or message.author.name} has ID {lookupDestinyID(message.author.id)}')



class unregister(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] function to delete Users from the database"
        params = ['discordID']
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message) and not message.author.id == params[0]:
            return

        if removeUser(params[0]):
            await message.author.send(f'removed {params[0]}')
        else:
            await message.author.send('removal failed for ', params[0])
