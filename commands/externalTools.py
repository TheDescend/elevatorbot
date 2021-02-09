
from discord.ext import commands

from commands.base_command import BaseCommand
from functions.dataLoading import updateDB
from functions.database import lookupDestinyID, getSystemAndChars, lookupSystem
from functions.formating import embed_message

rrsystem = {
    1: 'xb',
    2: 'ps',
    3: 'pc'
}

class RR(BaseCommand):
    def __init__(self):
        description = "Gets your personal raid.report link"
        topic = "Destiny"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        destinyID = lookupDestinyID(mentioned_user.id)
        system = lookupSystem(destinyID)

        if not (destinyID and system):
            await message.channel.send(embed=embed_message(
                'Error',
                f'Problem getting your data, please `!registerdesc` to fix this'
            ))

        await message.channel.send(embed=embed_message(
            'Raid Report',
            f'https://raid.report/{rrsystem[system]}/{destinyID}'
        ))


class DR(BaseCommand):
    def __init__(self):
        description = "Gets your personal dungeon.report link"
        topic = "Destiny"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        destinyID = lookupDestinyID(mentioned_user.id)
        system = lookupSystem(destinyID)

        if not (destinyID and system):
            await message.channel.send(embed=embed_message(
                'Error',
                f'Problem getting your data, please `!registerdesc` to fix this'
            ))

        await message.channel.send(embed=embed_message(
            'Dungeon Report',
            f'https://dungeon.report/{rrsystem[system]}/{destinyID}'
        ))


class GR(BaseCommand):
    def __init__(self):
        description = "Gets your personal grandmaster.report link"
        topic = "Destiny"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        destinyID = lookupDestinyID(mentioned_user.id)
        system = lookupSystem(destinyID)

        if not (destinyID and system):
            await message.channel.send(embed=embed_message(
                'Error',
                f'Problem getting your data, please `!registerdesc` to fix this'
            ))

        await message.channel.send(embed=embed_message(
            'Grandmaster Report',
            f'https://grandmaster.report/user/{system}/{destinyID}'
        ))


class NR(BaseCommand):
    def __init__(self):
        description = "Gets your personal nightfall.report link"
        topic = "Destiny"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        destinyID = lookupDestinyID(mentioned_user.id)
        system = lookupSystem(destinyID)

        if not (destinyID and system):
            await message.channel.send(embed=embed_message(
                'Error',
                f'Problem getting your data, please `!registerdesc` to fix this'
            ))

        await message.channel.send(embed=embed_message(
            'Nightfall Report',
            f'https://nightfall.report/guardian/{system}/{destinyID}'
        ))


class TR(BaseCommand):
    def __init__(self):
        description = "Gets your personal destinytrialsreport link"
        topic = "Destiny"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        destinyID = lookupDestinyID(mentioned_user.id)
        system = lookupSystem(destinyID)

        if not (destinyID and system):
            await message.channel.send(embed=embed_message(
                'Error',
                f'Problem getting your data, please `!registerdesc` to fix this'
            ))

        await message.channel.send(embed=embed_message(
            'Trials Report',
            f'https://destinytrialsreport.com/report/{system}/{destinyID}'
        ))
