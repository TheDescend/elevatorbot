from commands.base_command          import BaseCommand
from functions.authfunctions        import getRasputinQuestProgress

import discord
import pandas as pd
from datetime import datetime

class rasputin(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[depracted] Used to show the percentage of quest progress"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        # rembed = discord.Embed(
        #     title = 'Rasputin PE progress',
        #     set_author = 'Hali',
        # )
        # for objname, objprogress, objtotal in getRasputinQuestProgress():
        #     rembed = rembed.add_field(name = objname, value = f"{objprogress:,}\n{objprogress/objtotal*100:5.2f}%")
        # rembed = rembed.add_field(name = objname, value = f"out of {objtotal:,}", inline=False)
        # await message.channel.send(embed = rembed)
        await message.channel.send("The Lie has been completed, visit Ana for further steps")


class rasputinGraph(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Shows the timeline of seraph-completions"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        rdata = pd.read_pickle('database/rasputinData.pickle')
        rdata = rdata.set_index('datetime').resample('15T').mean()

        rdata = rdata.assign(edz=rdata.edz.interpolate(method='quadratic'))
        rdata = rdata.assign(moon=rdata.moon.interpolate(method='quadratic'))
        rdata = rdata.assign(io=rdata.io.interpolate(method='quadratic'))

        fig = rdata.plot().get_figure()
        filename = f'rasputin_{datetime.now().strftime("%Y_%m_%d__%H_%M")}.png'
        fig.savefig(filename)
        with open(filename, 'rb') as fp:
            imagefile = discord.File(fp, 'graph.png')
            await message.channel.send(file=imagefile)
