from typing import Union

import discord
from discord_slash import ButtonStyle
from discord_slash.utils import manage_components

from commands.base_command import BaseCommand
from database.database import removeUser, lookupDestinyID
from functions.formating import embed_message
from functions.miscFunctions import hasAdminOrDevPermissions
from static.config import BUNGIE_OAUTH

# has been slashified
class register(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Register with bungie.net"
        params = []
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        if not message.guild:
            await message.author.send('Please use this command in your clans bot-channel')
            return
        await elevatorRegistration(message.author)

# has been slashified
class registerDesc(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Shadows !register, but don't get picked up from Charlemange"
        params = []
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        if not message.guild:
            await message.author.send('Please use this command in your clans bot-channel')
            return
        await elevatorRegistration(message.author)


async def elevatorRegistration(user: discord.Member):
    URL = f"https://www.bungie.net/en/oauth/authorize?client_id={BUNGIE_OAUTH}&response_type=code&state={str(user.id) + ':' + str(user.guild.id)}"

    components = [
        manage_components.create_actionrow(
            manage_components.create_button(
                style=ButtonStyle.URL,
                label=f"Registration Link",
                url=URL
            ),
        ),
    ]

    await user.send(components=components, embed=embed_message(
        f'Registration',
        f'Use the button below to register with me',
        "Please be aware that I will need a while to process your data after you register for the first time, so I might react very slow to your first commands."
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
    async def handle(self, params, message, mentioned_user, client):
        await message.channel.send(f'User {mentioned_user.nick or mentioned_user.name} has ID {lookupDestinyID(mentioned_user.id)}')


# has been slashified
class unregister(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Unregister from ElevatorBot"
        params = []
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message) and not message.author.id == mentioned_user.id:
            return

        await removeUser(mentioned_user.id)
        await message.author.send(f'removed {mentioned_user.nick or mentioned_user.name}')

