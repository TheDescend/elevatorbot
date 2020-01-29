from commands.base_command  import BaseCommand

from functions              import getIntStat, getUserMap, getUserIDbySnowflakeAndClanLookup, getFullMemberMap

import discord

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

        destinyID = getUserMap(message.author.id)
        if not destinyID:
            destinyID = getUserIDbySnowflakeAndClanLookup(message.author, getFullMemberMap())

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
        
        elif name == 'help':
            await message.channel.send(f'''
            {message.author.mention}, use those arguments for !stat *<argument>*
            > **resurrections**: *Shows how many players you revived and how many times you got revived*
            > **meleekills**: *Shows how many enemies you've punched to death*
            > **superkills**: *Shows how many enemies you've killed with your super*
            > **longrangekill**: *Shows how far you've sniped*
            ''')
        else:
            await message.channel.send('Use !stat help for a list of commands :)')
