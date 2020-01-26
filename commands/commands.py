from commands.base_command import BaseCommand


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
        msg += "Contact <@171650677607497730> if any problems arise\n"
        # Displays all descriptions, sorted alphabetically by command name
        for cmd in sorted(COMMAND_HANDLERS.items()):
            if not '[dev]' in cmd[1].description and not '[depracted]' in cmd[1].description:
                msg += "\n" + cmd[1].description

        await message.channel.send(msg)
