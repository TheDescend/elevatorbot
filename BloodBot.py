#!/usr/bin/env python3
import sys

import discord
import message_handler

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from events.base_event              import BaseEvent
from events                         import *
from functions.roles                import assignRolesToUser
from functions.bounties.bountiesFunctions import generateBounties, registrationMessageReactions
from commands.otherGameRoles import otherGameRolesMessageReactions
import asyncio
import datetime
import random
import re
import os
import pickle

from discord.ext.commands import Bot

from threading import Thread
from threading import current_thread

from functions.database import insertIntoMessageDB
from static.config      import NOW_PLAYING, COMMAND_PREFIX, BOT_TOKEN
from functions.formating import embed_message

# Set to remember if the bot is already running, since on_ready may be called
# more than once on reconnects
this = sys.modules[__name__]
this.running = False

# Scheduler that will be used to manage events
sched = AsyncIOScheduler()


###############################################################################

def launch_event_loops(client):
    print("Loading events...", flush=True)
    n_ev = 0
    for ev in BaseEvent.__subclasses__():
        event = ev()
        sched.add_job(event.run, 'interval', (client,),
                        minutes=event.interval_minutes)
        n_ev += 1

    # generate new bounties every monday at midnight
    #sched.add_job(generateBounties, "cron", (client,), day_of_week="thu", hour=15, minute=28)
    sched.add_job(generateBounties, "cron", (client,), day_of_week="mon", hour=0, minute=0)

    sched.start()
    print(f"{n_ev} events loaded", flush=True)
    print(f"Startup complete!", flush=True)


def main():
    """the main method"""
    # Initialize the client
    print("Starting up...")
    client = Bot('!')

    # Define event handlers for the client
    # on_ready may be called multiple times in the event of a reconnect,
    # hence the running fla
    @client.event
    async def on_ready():
        if this.running:
            return

        this.running = True

        # Set the playing status
        if NOW_PLAYING:
            print("Setting NP game", flush=True)
            await client.change_presence(
                activity=discord.Game(name=NOW_PLAYING))
        print("Logged in!", flush=True)

        t1 = Thread(target=launch_event_loops, args=(client,))
        t1.start()


    # The message handler for both new message and edits
    @client.event
    async def common_handle_message(message):
        text = message.content
        if 'äbidöpfel' in text:
            texts = [   '<:NeriaHeart:671389916277506063> <:NeriaHeart:671389916277506063> <:NeriaHeart:671389916277506063>', 
                        'knows what`s up', 'knows you can do the thing', 'has been voted plushie of the month', 'knows da wey',
                        'yes!', 'does`nt yeet teammtes of the map, be like Häbidöpfel', 'debuggin has proven effective 99.9% of the time',
                        'is cuteness incarnate']
            addition = random.choice(texts)
            await message.channel.send(f'Häbidöpfel {addition}')
        if "welcome" in text.lower() and "<@!109022023979667456>" in text.lower():
            await message.channel.send(f'Welcome <@109022023979667456>!')
        if text.startswith(COMMAND_PREFIX) and text != COMMAND_PREFIX:
            cmd_split = text[len(COMMAND_PREFIX):].split()
            try:
                await message_handler.handle_command(cmd_split[0].lower(),
                                      cmd_split[1:], message, client)
            except:
                print("Error while handling message", flush=True)
                raise
        else:
            badwords = ['kanen', 'cyber', 'dicknugget', 'nigg', 'cmonbrug', ' bo ', 'bloodoak', 'ascend', 'cock', 'cunt']
            goodchannels = [
                670400011519000616, #general
                670400027155365929, #media
                670402166103474190, #spoiler-chat
                670362162660900895, #off-topic
                #672541982157045791 #markov-chat-channel
                ] 
            if not message.content.startswith('http') and len(message.clean_content) > 5 and not any([badword in message.clean_content.lower() for badword in badwords]) and message.channel.id in goodchannels:
                formattedtime = message.created_at.strftime('%Y-%m-%dT%H:%M')
                success = insertIntoMessageDB(message.clean_content,message.author.id,message.channel.id,message.id, formattedtime)
        
        if message.author.name == 'EscalatorBot':
            for user in message.mentions:
                member = message.guild.get_member(user.id)
                await member.add_roles(message.guild.get_role(670396064007979009))
                await member.remove_roles(message.guild.get_role(670396109088358437))
                await message.channel.send(f'{member.mention} has been marked as Registered')
                await member.send('Registration successful!\nCome say hi in <#670400011519000616>')

    tasks = []
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        asyncio.ensure_future(common_handle_message(message))

    @client.event
    async def on_member_join(member):
        guestObj = discord.utils.get(member.guild.roles, name="Guest")
        await member.add_roles(guestObj)

        # inform the user that they should register with the bot
        await member.send(embed=embed_message(
            f'Welcome to Descend {member.name}!',
            f'Please link your Destiny account by using `!register` in #bot-spam. \n We have a wide variety of roles you can earn, for more information, check out #community-roles.',
            f'If you have any questions, please contact one of the Admins / Moderators'
        ))

        # add @Not Registered to user
        await assignRolesToUser(["Not Registered"], member, member.guild)

    @client.event
    async def on_message_edit(before, after):
        await common_handle_message(after)

    # https://discordpy.readthedocs.io/en/latest/api.html#discord.RawReactionActionEvent
    @client.event
    async def on_raw_reaction_add(payload):
        if payload.member.bot:
            return

        # for checking reactions to the bounties registration page
        if os.path.exists('functions/bounties/channelIDs.pickle'):
            with open('functions/bounties/channelIDs.pickle', "rb") as f:
                file = pickle.load(f)

            # check if reaction is on the registration page
            if "register_channel_message_id" in file:
                register_channel_message_id = file["register_channel_message_id"]
                if payload.message_id == register_channel_message_id:
                    register_channel = discord.utils.get(client.get_all_channels(), guild__id=payload.guild_id, id=file["register_channel"])
                    await registrationMessageReactions(payload.member, payload.emoji, register_channel, register_channel_message_id)

            # check if reaction is on the other game role page
            if "other_game_roles_channel_message_id" in file:
                other_game_roles_channel_message_id = file["other_game_roles_channel_message_id"]
                if payload.message_id == other_game_roles_channel_message_id:
                    register_channel = discord.utils.get(client.get_all_channels(), guild__id=payload.guild_id, id=file["other_game_roles_channel"])
                    await otherGameRolesMessageReactions(client, payload.member, payload.emoji, register_channel, other_game_roles_channel_message_id)



    @client.event
    async def on_voice_state_update(member, before, after):
        if before.channel is None:
            #print(f'{member.name} joined VC {after.channel.name}')
            await joined_channel(member, after.channel)
            return

        if after.channel is None:
            #print(f'{member.name} left VC {before.channel.name}')
            await left_channel(member, before.channel)
            return

        if before.channel != after.channel:
            #print(f'{member.name} changed VC from {before.channel.name} to {after.channel.name}')
            await joined_channel(member, after.channel)
            await left_channel(member, before.channel)
            return

    async def joined_channel(member, channel):
        nummatch = re.findall(r'\d\d', channel.name)
        if nummatch:
            number = int(nummatch[-1])
            nextnumber = number + 1
            if nextnumber == 8:
                #await member.send('What the fuck are you doing')
                return
            nextnumberstring = str(nextnumber).zfill(2)

            channelnamebase = channel.name.replace(nummatch[-1], '')

            if not discord.utils.get(member.guild.voice_channels, name=channelnamebase + nextnumberstring):
                await channel.clone(name=channelnamebase + nextnumberstring)
                newchannel = discord.utils.get(member.guild.voice_channels, name=channelnamebase + nextnumberstring)
                await newchannel.edit(position=channel.position + 1)
                if 'PVP' in channel.name:
                    await newchannel.edit(position=channel.position + 1, user_limit=6)
       
    
    async def left_channel(member, channel):
        defaultchannels = 2
        nummatch = re.findall(r'\d\d', channel.name)
        if nummatch:
            number = int(nummatch[-1])
            previousnumber = number - 1
            previousnumberstring = str(previousnumber).zfill(2)

            channelnamebase = channel.name.replace(nummatch[-1], '')
            
            achannel = channel
            while achannel is not None:
                number = number + 1
                achannel = discord.utils.get(member.guild.voice_channels, name=channelnamebase + str(number).zfill(2))
            number = number - 1

            for i in range(defaultchannels+1, number+1, 1):
                higher = discord.utils.get(member.guild.voice_channels, name=channelnamebase + str(i).zfill(2))
                below = discord.utils.get(member.guild.voice_channels, name=channelnamebase + str(i - 1).zfill(2))
                if higher and not higher.members:
                    if below and not below.members:
                        await higher.delete()
            
            for i in range(defaultchannels+1, number + 1, 1):
                higher = discord.utils.get(member.guild.voice_channels, name=channelnamebase + str(i).zfill(2))
                below = discord.utils.get(member.guild.voice_channels, name=channelnamebase + str(i - 1).zfill(2))
                if higher and not below:
                        await higher.edit(name=channelnamebase + str(i-1).zfill(2))

    # Finally, set the bot running
    client.run(BOT_TOKEN)

###############################################################################


if __name__ == "__main__":
    # p = Process(target=start_server)
    # p.start()
    # print('server started')

    main()

    #p.join()
