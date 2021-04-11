from commands.base_command import BaseCommand
from functions.database import removeUser, lookupDestinyID
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
        await elevatorRegistration(message)

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
        await elevatorRegistration(message)


async def elevatorRegistration(message):
    if not message.guild:
        await message.author.send('Please use this command in your clans bot-channel')
        return
    state = str(message.author.id) + ':' + str(message.guild.id)
    URL = f'https://www.bungie.net/en/oauth/authorize?client_id={BUNGIE_OAUTH}&response_type=code&state={state}'
    await message.author.send(embed=embed_message(
        f'Registration',
        f'[Click here to register with me]({URL})',
        "Please be aware that I will need a while to process your data after you register for the first time, so I might react very slow to your first commands."
    ))
    await message.channel.send(embed=embed_message(
        'Registration',
        f'Sent a DM to {message.author.nick or message.author.name}'
    ))


# todo: slashify when you can hide commands
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

        if removeUser(mentioned_user.id):
            await message.author.send(f'removed {mentioned_user.nick or mentioned_user.name}')
        else:
            await message.author.send('removal failed for ', {mentioned_user.nick or mentioned_user.name})
