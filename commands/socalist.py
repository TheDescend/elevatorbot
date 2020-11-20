from commands.base_command import BaseCommand


class socialist(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Spams #socialist"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        await message.channel.send("No 🙃")
