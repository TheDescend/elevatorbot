from discord.ext.commands import Bot

client = None

def init_client():
    global client
    client = Bot('!')