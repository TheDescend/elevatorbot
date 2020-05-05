from commands.base_command  import BaseCommand

from functions.database import getEverything
from discord import File

class dumpdb(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[Debug] Dumps db contents"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        with open("database/userdb.sqlite3", "rb") as fp:
            await message.channel.send(file=File(fp))


