from commands.base_command  import BaseCommand
from functions.bounties.bountiesFunctions import saveAsGlobalVar


class bountiesMakeChannelRegister(BaseCommand):
    def __init__(self):
        description = f'Admin / Dev only'
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        saveAsGlobalVar("register_channel", message.channel.id)
        await message.channel.send("Done!")

class bountiesMakeChannelLeaderboard(BaseCommand):
    def __init__(self):
        description = f'Admin / Dev only'
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        saveAsGlobalVar("leaderboard_channel", message.channel.id)
        await message.channel.send("Done!")

class bountiesMakeChannelBounties(BaseCommand):
    def __init__(self):
        description = f'Admin / Dev only'
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        saveAsGlobalVar("bounties_channel", message.channel.id)
        await message.channel.send("Done!")

class bountiesMakeChannelTournament(BaseCommand):
    def __init__(self):
        description = f'Admin / Dev only'
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        saveAsGlobalVar("tournament_channel", message.channel.id)
        await message.channel.send("Done!")
