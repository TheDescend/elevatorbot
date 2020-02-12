from commands.base_command  import BaseCommand

from markovGenerator        import getMarkovSentence
from database               import db_connect

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

class finish(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Generates a random message, based on past conversations in this server"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        startword = message.clean_content.split(' ')[-1]
        sentence = ' '.join(message.clean_content.split(' ')[1:])
        async with message.channel.typing():
            await message.channel.send(sentence + ' ' + getMarkovSentence(startword))


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

class updateDB(BaseCommand):
    def __init__(self):
        description = "[dev] Updates the DB from the Descend Discord"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        conn = db_connect()
        c = conn.cursor()
        c.execute('''DELETE FROM markovpairs''')#TRUNCATE
        conn.commit()
        c.execute('''
        SELECT msg FROM messagedb
        ''')
        text = list(c.fetchall())
        for dbquery in text:
            sentence = dbquery[0]
            words = sentence.split(' ')
            sentenceedges = zip(['__start__'] + words, words + ['__end__'])
            for (a,b) in sentenceedges:
                    conn.execute(f'''
                    INSERT INTO markovpairs 
                    (word1, word2) 
                    VALUES 
                    (?,?)
                    ''',(a,b))
        conn.commit()
        
        await message.channel.send('updated markov table') #newtonslab

# general = 670400011519000616
# media = 670400027155365929
# spoilerchat = 670402166103474190
# offtopic = 670362162660900895