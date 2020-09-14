from commands.base_command import BaseCommand
import re

# This is a convenient command that automatically generates a helpful
# message showing all available commands
class Commands(BaseCommand):

    def __init__(self):
        description = "Displays this help message"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        if message.author.id == 367385031569702912:
            await message.channel.send('<@367385031569702912> :Pepega:670369123716431872')
        from message_handler import COMMAND_HANDLERS
        msg = message.author.mention + "\n"
        msg += "Contact <@670397357120159776> if any problems arise\n"
        tagfinder = re.compile(r'\[[A-Za-z]*\]')
        # Displays all descriptions, sorted alphabetically by command name
        for cmd in sorted(COMMAND_HANDLERS.items()):
            if not tagfinder.search(cmd[1].description) or message.channel.id == 670637036641845258:
                msg += "\n" + cmd[1].description

        for i in range(len(msg)//2000):
            await message.channel.send(msg[i*2000:(i+1)*2000])

class Documentation(BaseCommand):

    def __init__(self):
        description = "[dev] Displays a link to the documentation"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        message.channel.send('Check out https://github.com/LukasSchmid97/destinyBloodoakStats/blob/master/README.md')