from commands.base_command  import BaseCommand
from functions.bounties.bountiesFunctions import saveAsGlobalVar, deleteFromGlobalVar, bountiesChannelMessage


class bountiesMakeChannelRegister(BaseCommand):
    def __init__(self):
        description = f'[dev] Admin / Dev only'
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        deleteFromGlobalVar("register_channel_message_id")
        saveAsGlobalVar("register_channel", message.channel.id, message.guild.id)
        await bountiesChannelMessage(client)


class bountiesMakeChannelLeaderboard(BaseCommand):
    def __init__(self):
        description = f'[dev] Admin / Dev only'
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        deleteFromGlobalVar("leaderboard_channel_message_id")
        saveAsGlobalVar("leaderboard_channel", message.channel.id, message.guild.id)
        await bountiesChannelMessage(client)


# class bountiesMakeChannelBounties(BaseCommand):
#     def __init__(self):
#         description = f'Admin / Dev only'
#         params = []
#         super().__init__(description, params)
#
#     async def handle(self, params, message, client):
#         saveAsGlobalVar("bounties_channel", message.channel.id, message.guild.id)
#         await message.channel.send("Done!")
#

# class bountiesMakeChannelTournament(BaseCommand):
#     def __init__(self):
#         description = f'Admin / Dev only'
#         params = []
#         super().__init__(description, params)
#
#     async def handle(self, params, message, client):
#         saveAsGlobalVar("tournament_channel", message.channel.id, message.guild.id)
#         await message.channel.send("Done!")
