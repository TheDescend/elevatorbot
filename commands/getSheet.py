from commands.base_command  import BaseCommand
from io import open
from spreadsheets.generateFastAchievementList import createSheet
from functions.roles import hasAdminOrDevPermissions

import os
import time
import discord

class getSheet(BaseCommand):

    lastupdate = 0.0
    sheetpath = None

    def __init__(self):
        # A quick description for the help message
        self.lastupdate = 0.0
        self.sheetpath = None
        description = "[depracted] gets the reduced Spreadsheet"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer') 

        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message) and not message.author.id == params[0]:
            return


        if time.time() - self.lastupdate < 86400:
            if self.sheetpath is not None:
                f = discord.File(open(self.sheetpath,'rb'),'AchievementSheet.xlsx')
                await message.channel.send('Recently generated one, take this instead')
                await message.channel.send(file=f)
                return
            print('couldn\'t find old sheet, even though it should exist')

        #tell the user it's processing and create sheet
        await message.channel.send('This is gonna take a loooooooong time')
        async with message.channel.typing():
            self.sheetpath = await createSheet()
            if self.sheetpath is not None:
                f = discord.File(open(self.sheetpath,'rb'),'AchievementSheet.xlsx')
                await message.channel.send(file=f)
                await message.channel.send('There you go! Thanks for waiting')
                self.lastupdate = time.time()
            else:
                await message.channel.send('Something went wrong')

