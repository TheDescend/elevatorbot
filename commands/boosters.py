
from commands.base_command  import BaseCommand


class boosters(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Prints all premium subscribers"
        params = []
        super().__init__(description, params)
    
    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        await message.channel.send(", ".join([m.name for m in message.guild.premium_subscribers]))

