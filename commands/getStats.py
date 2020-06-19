from commands.base_command          import BaseCommand

from functions.dataLoading          import getCharacterList, getCharactertypeList
from functions.dataTransformation   import getIntStat, getCharStats, getFullMemberMap,getTop10PveGuns, getGunsForPeriod, getPossibleStats
from functions.authfunctions        import getSpiderMaterials
from functions.database             import lookupDestinyID, getToken

import discord
import os

class stat(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Gives you stats for your account. Use !stat help for a list of possible values"
        params = ['statName']
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        name = params[0]

        destinyID = lookupDestinyID(message.author.id)
        if not destinyID:
            await message.channel.send(f'Unable to get your destiny-stats. Please contact a {message.guild.get_role(670397357120159776)}')
            return
        if name == 'resurrections': #
            given = getIntStat(destinyID, 'resurrectionsPerformed')
            received = getIntStat(destinyID, 'resurrectionsReceived')
            await message.channel.send(f'{message.author.mention}, you have revived **{given}** people and got revived **{received}** times! 🚑')

        elif name == 'meleekills':
            melees = getIntStat(destinyID, 'weaponKillsMelee')
            await message.channel.send(f'{message.author.mention}, you have punched **{melees}** enemies to death! 🖍️')

        elif name == 'superkills':
            melees = getIntStat(destinyID, 'weaponKillsSuper')
            await message.channel.send(f'{message.author.mention}, you have used your supers to extinguish **{melees}** enemies! <a:PepoCheer:670678495923273748>')

        elif name == 'longrangekill':
            snips = getIntStat(destinyID, 'longestKillDistance')
            await message.channel.send(f'{message.author.mention}, you sniped an enemy as far as **{snips}** meters away <:Kapp:670369121808154645>')
        elif name == 'top10pveguns':
            async with message.channel.typing():
                imgpath = getTop10PveGuns(destinyID)
                with open(imgpath, 'rb') as f:
                    await message.channel.send(f'{message.author.mention}, here are your top10 guns used in raids', file=discord.File(f))
                os.remove(imgpath)
        elif name == 'pve': #starttime endtime
            start = params[1]
            end = params[2]
            await message.channel.send(getGunsForPeriod(destinyID, start, end))
            #"2020-03-31"
        elif name == 'deaths':
            stats = []
            for charid, chardesc in getCharactertypeList(destinyID):
                stats.append((chardesc, getCharStats(destinyID, charid, 'deaths')))
            printout = "\n".join([f'Your {chardesc} has {"{:,}".format(count)} deaths' for chardesc,count in stats])
            await message.channel.send(printout)
        elif name == 'help':
            await message.channel.send(f'''
            {message.author.mention}, use those arguments for !stat *<argument>*:
            > **resurrections**: *Shows how many players you revived and how many times you got revived*
            > **meleekills**: *Shows how many enemies you've punched to death*
            > **superkills**: *Shows how many enemies you've killed with your super*
            > **longrangekill**: *Shows how far you've sniped*
            > **top10raidguns**: *Shows a piechart of your favourite guns* 
             other possible stats include {", ".join(getPossibleStats())}
             ''')
        elif name in getPossibleStats():
            stats = []
            for charid, chardesc in getCharactertypeList(destinyID):
                stats.append((chardesc, getCharStats(destinyID, charid, name)))
            printout = "\n".join([f'Your {chardesc} has {"{:,}".format(int(count))} {name}' for chardesc,count in stats])
            await message.channel.send(printout)
        else:
            await message.channel.send('Use !stat help for a list of commands :)')

class spoder(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Gives the spoders inventory"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        discordID = message.author.id
        destinyID = lookupDestinyID(discordID)
        anyCharID = getCharacterList(destinyID)[1][0]

        async with message.channel.typing():
            materialtext = getSpiderMaterials(discordID, destinyID, anyCharID)
            if materialtext:
                await message.channel.send(materialtext)