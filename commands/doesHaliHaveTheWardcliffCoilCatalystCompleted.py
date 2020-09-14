from commands.base_command  import BaseCommand

from functions.dataTransformation import hasTriumph

class doesHaliHaveTheWardcliffCoilCatalystCompleted(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Does he?"
        topic = "Destiny"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        text = 'no, but <@109022023979667456> does'
        if hasTriumph(4611686018468695677, 543481464):
            text = 'yes'
        await message.channel.send(text)