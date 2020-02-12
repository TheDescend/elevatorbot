import sys

import config
import discord
import message_handler

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from events.base_event              import BaseEvent
from events                         import *
from multiprocessing                import Process
import asyncio
import datetime

from oauth import start_server
from database import insertIntoMessageDB

# Set to remember if the bot is already running, since on_ready may be called
# more than once on reconnects
this = sys.modules[__name__]
this.running = False

# Scheduler that will be used to manage events
sched = AsyncIOScheduler()


###############################################################################

def main():
    # Initialize the client
    print("Starting up...")
    client = discord.Client()
    # Define event handlers for the client
    # on_ready may be called multiple times in the event of a reconnect,
    # hence the running fla
    @client.event
    async def on_ready():
        if this.running:
            return

        this.running = True

        # Set the playing status
        if config.NOW_PLAYING:
            print("Setting NP game", flush=True)
            await client.change_presence(
                activity=discord.Game(name=config.NOW_PLAYING))
        print("Logged in!", flush=True)

        # Load all events
        print("Loading events...", flush=True)
        n_ev = 0
        for ev in BaseEvent.__subclasses__():
            event = ev()
            sched.add_job(event.run, 'interval', (client,),
                          minutes=event.interval_minutes)
            n_ev += 1
        sched.start()
        print(f"{n_ev} events loaded", flush=True)
        print(f"Startup complete!", flush=True)

    # The message handler for both new message and edits
    @client.event
    async def common_handle_message(message):
        text = message.content
        if text.startswith(config.COMMAND_PREFIX) and text != config.COMMAND_PREFIX:
            cmd_split = text[len(config.COMMAND_PREFIX):].split()
            try:
                await message_handler.handle_command(cmd_split[0].lower(), 
                                      cmd_split[1:], message, client)
            except:
                print("Error while handling message", flush=True)
                raise
        else:
            badwords = ['kanen', 'cyber', 'dicknugget', 'nigg', 'cmonbrug', ' bo ', 'bloodoak', 'ascend', 'cock', 'cunt']
            goodchannels = [670400011519000616, 670400027155365929, 670402166103474190, 670362162660900895, 672541982157045791]
            if not message.content.startswith('http') and len(message.clean_content) > 5 and not any([badword in message.clean_content.lower() for badword in badwords]) and message.channel.id in goodchannels:
                formattedtime = message.created_at.strftime('%Y-%m-%dT%H:%M')
                success = insertIntoMessageDB(message.clean_content,message.author.id,message.channel.id,message.id, formattedtime)

    tasks = []
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        asyncio.ensure_future(common_handle_message(message))

    @client.event
    async def on_message_edit(before, after):
        await common_handle_message(after)

    # Finally, set the bot running
    client.run(config.BOT_TOKEN)

###############################################################################


if __name__ == "__main__":
    # p = Process(target=start_server)
    # p.start()
    # print('server started')

    main()

    #p.join()
