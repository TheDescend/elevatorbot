from commands.base_command import BaseCommand


class muteMe(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Starts the counting challenge"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        await message.channel.send("Start counting, first person has to begin with 1")

        i = 1
        while True:
            # wait for the next message in the channel
            def check(m):
                return m.channel == message.channel
            msg = await client.wait_for('message', check=check)

            # check if he counted up correctly
            if msg.content != str(i):
                await message.channel.send(f"{msg.author.mention} ruined it at {str(i-1)}")
                return

            i += 1
