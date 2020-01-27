from commands.base_command  import BaseCommand

import discord

class socialists(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Assigns you all the roles you've earned"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        await message.delete()
        channelID = 670573554315690007
        socialistID = 671444789664677888
        forthesocialism = client.get_channel(channelID)
        socialist = message.guild.get_role(670579222468755458)
        msg = ''
        for i in range(80):
            msg += socialist.mention + ' '
        for k in range(20):
            await forthesocialism.send(msg)

