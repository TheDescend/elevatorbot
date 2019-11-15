from commands.base_command  import BaseCommand
from io import open
from Spreadsheet2 import createSheet

import os
from discord import File

class getSheet(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "gets the reduced Spreadsheet"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        async with message.channel.typing():
            await message.channel.send('This is gonna take a loooooooong time')
            sheetpath = createSheet()
            if sheetpath is not None:
                f = File(open(sheetpath,'rb'),'AchievementSheet.xlsx')
                await message.channel.send(file=f)
            await message.channel.send('There you go! Thanks for waiting')

