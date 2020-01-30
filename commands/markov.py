from commands.base_command  import BaseCommand

from markovGenerator        import getMarkovSentence

import discord
import os

class markov(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Generates a random message, based on past conversations in this server"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        async with message.channel.typing():
            await message.channel.send(getMarkovSentence())

class initiateDB(BaseCommand):
    def __init__(self):
        description = "[dev] Creates the DB from the Descend Discord"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        if message.author.id == 171650677607497730:
            for chnlid in [670400011519000616, 670400027155365929, 670402166103474190, 670362162660900895]:
                chnl = client.get_channel(chnlid)
                async for msg in chnl.history(limit=None):
                    if not msg.content.startswith('http') and not msg.content.startswith('!') and len(msg.clean_content) > 5 :
                        formattedtime = msg.created_at.strftime('%Y-%m-%dT%H:%M')
                        success = insertIntoMessageDB(msg.clean_content,msg.author.id,msg.channel.id,msg.id, formattedtime)
                await message.channel.send(f'working on {chnl.name}')


# general = 670400011519000616
# media = 670400027155365929
# spoilerchat = 670402166103474190
# offtopic = 670362162660900895