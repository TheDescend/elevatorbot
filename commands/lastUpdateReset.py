from discord.ext import commands

from commands.base_command import BaseCommand
from functions.database import setMembersLastUpdated
from functions.miscFunctions import hasAdminOrDevPermissions

from datetime import datetime


# todo: slashify when you can hide commands
class setLastUpdated(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[admin] set all users lastUpdated to year, month, day"
        params = ["year", "month", "day"]
        topic = "Roles"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        if not await hasAdminOrDevPermissions(message):
            return

        targetdate = datetime(int(params[0]), int(params[1]), int(params[2]), 0, 0)
        setMembersLastUpdated(targetdate)
        await message.channel.send(f'Successfully set lastUpdated to {targetdate.strftime("%d/%m/%Y")}')