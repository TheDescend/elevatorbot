from commands.base_command import BaseCommand

class startCounting(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Starts the counting challenge"
        params = []
        super().__init__(description, params)

    # Override the handle() methodget
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        await message.channel.send("Start counting, first person has to begin with `1`")

        i = 1
        last_msg = None
        while True:
            # wait for the next message in the channel
            def check(m):
                return m.channel == message.channel
            msg = await client.wait_for('message', check=check)

            # check if author was the one from the last successful count
            if msg.author == last_msg:
                await message.channel.send(f"You can't send two numbers in a row!")
                continue

            # check if he counted up correctly
            if msg.content != str(i):
                await message.channel.send(f"{msg.author.mention} ruined it at `{str(i-1)}`")
                return

            # count up and set new last user
            last_msg = msg.author
            i += 1
