from commands.base_command  import BaseCommand
from io import open
from generateFastAchievementList import createSheet

import os
from discord import File
import time

class getSheet(BaseCommand):

    lastupdate = 0.0
    sheetpath = None

    def __init__(self):
        # A quick description for the help message
        self.lastupdate = 0.0
        self.sheetpath = None
        description = "gets the reduced Spreadsheet"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        #generating sheet at max every 12 hours
        if (time.time() - self.lastupdate) < 86400.0:
            if self.sheetpath is not None:
                f = File(open(self.sheetpath,'rb'),'AchievementSheet.xlsx')
                await message.channel.send('Recently generated one, take this instead')
                await message.channel.send(file=f)
                return
            print('couldn\'t find old sheet, even though it should exist')

        #tell the user it's processing and create sheet
        await message.channel.send('This is gonna take a loooooooong time')
        async with message.channel.typing():
            self.sheetpath = createSheet()
            if self.sheetpath is not None:
                f = File(open(self.sheetpath,'rb'),'AchievementSheet.xlsx')
                await message.channel.send(file=f)
                await message.channel.send('There you go! Thanks for waiting')
                self.lastupdate = time.time()
            else:
                await message.channel.send('Something went wrong')

