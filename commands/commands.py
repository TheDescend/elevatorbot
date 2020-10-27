import re

from commands.base_command import BaseCommand
# This is a convenient command that automatically generates a helpful
# message showing all available commands
from static.globals import dev_role_id


class Commands(BaseCommand):

    def __init__(self):
        description = "Displays this help message"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        if message.author.id == 367385031569702912:
            await message.channel.send('<@!367385031569702912> :Pepega:670369123716431872')
        from message_handler import COMMAND_HANDLERS
        msg = f"Contact <@&{dev_role_id}> if any problems arise\n⁣\n"

        #admin = await hasAdminOrDevPermissions(message, send_message=False)
        admin = (message.channel.id == 670637036641845258)

        # sort by topic
        commands_by_topic = {}
        for cmd in sorted(COMMAND_HANDLERS.items()):
            description = cmd[1].description
            braces = re.compile(r'\[[A-Za-z]+\]')
            if (not braces.search(description)) or admin:
                topic = cmd[1].topic
                if topic not in commands_by_topic:
                    commands_by_topic[topic] = []
                commands_by_topic[topic].append(description)
        commands_by_topic = {k: v for k, v in sorted(commands_by_topic.items(), key=lambda item: item[0])}

        await message.channel.send(msg)

        for topic in commands_by_topic:
            msg = f"__{topic}__\n"
            msg += "\n".join(sorted(commands_by_topic[topic]))
            msg += "\n⁣\n"
            await message.channel.send(msg)

class Documentation(BaseCommand):

    def __init__(self):
        description = "[dev] Displays a link to the documentation"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        message.channel.send('Check out https://github.com/LukasSchmid97/destinyBloodoakStats/blob/master/README.md')