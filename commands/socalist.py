from commands.base_command import BaseCommand


# todo wait for perms, only allow for @socialists
class socialist(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Spams #socialist"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        await message.channel.send("No 🙃")
