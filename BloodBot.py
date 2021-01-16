#!/usr/bin/env python3
# import sys
# if "http" in sys.modules:
#     raise ImportError("Crawler must be imported before http module")
# import http.cookies
# http.cookies._is_legal_key = lambda _: True

import asyncio
import os
import random
import re
import sys
from io import BytesIO
from threading import Thread

import discord
import nltk
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import message_handler
from commands.makePersistentMessages import otherGameRolesMessageReactions, readRulesMessageReactions
from events.base_event import BaseEvent
from events import *
from functions.bounties.bountiesBackend import getGlobalVar
from functions.bounties.bountiesFunctions import registrationMessageReactions
from functions.clanJoinRequests import clanJoinRequestMessageReactions, removeFromClanAfterLeftDiscord
from functions.dataLoading import fillDictFromDB, updateDB
from functions.database import insertIntoMessageDB, db_connect, lookupDestinyID
from functions.formating import embed_message
from functions.miscFunctions import update_status
from functions.roles import assignRolesToUser, removeRolesFromUser
from init_logging import init_logging
from static.config import COMMAND_PREFIX, BOT_TOKEN
from static.dict import getNameFromHashRecords, getNameFromHashCollectible, getNameFromHashActivity, \
    getNameFromHashInventoryItem
from static.globals import guest_role_id, registered_role_id, not_registered_role_id, admin_discussions_channel_id, \
    divider_raider_role_id, divider_achievement_role_id, divider_misc_role_id, muted_role_id

nltk.download('vader_lexicon')
analyzer = SentimentIntensityAnalyzer()

#to enable the on_member_join and on_member_remove
intents = discord.Intents.default()
intents.members = True

# Set to remember if the bot is already running, since on_ready may be called
# more than once on reconnects
this = sys.modules[__name__]
this.running = False

# Scheduler that will be used to manage events
sched = AsyncIOScheduler()

charley_spam = "Please enter a valid leaderboard name. Type `!help rank` for more information."
###############################################################################

def launch_event_loops(client):
    print("Loading events...", flush=True)
    n_ev = 0
    for ev in BaseEvent.__subclasses__():
        event = ev()

        # check the type of job and schedule acordingly
        if event.scheduler_type == "interval":
            sched.add_job(event.run, 'interval', (client,), minutes=event.interval_minutes, jitter=60)
        elif event.scheduler_type == "cron":
            sched.add_job(event.run, 'cron', (client,), day_of_week=event.dow_day_of_week, hour=event.dow_hour, minute=event.dow_hour)
        elif event.scheduler_type == "date":
            sched.add_job(event.run, 'date', (client,), run_date=event.interval_minutes)

        n_ev += 1

    sched.start()
    print(f"{n_ev} events loaded", flush=True)
    print(f"Startup complete!", flush=True)


def main():
    """the main method"""

    # Initialize logging
    init_logging()

    # Connect to DB
    db_connect()

    # Initialize the client
    print("Starting up...")
    client = Bot('!', intents=intents)

    # Define event handlers for the client
    # on_ready may be called multiple times in the event of a reconnect,
    # hence the running fla
    @client.event
    async def on_ready():
        if this.running:
            return

        this.running = True

        t1 = Thread(target=launch_event_loops, args=(client,))
        t1.start()

        # getting manifest
        await fillDictFromDB(getNameFromHashRecords, 'DestinyRecordDefinition')
        await fillDictFromDB(getNameFromHashActivity, 'DestinyActivityDefinition')
        await fillDictFromDB(getNameFromHashCollectible, 'DestinyCollectibleDefinition')
        await fillDictFromDB(getNameFromHashInventoryItem, 'DestinyInventoryItemDefinition')

        print("Logged in!", flush=True)

        # Set the playing status
        await update_status(client)


    # The message handler for both new message and edits
    @client.event
    async def common_handle_message(message):
        text = message.content
        if charley_spam in text:
            await asyncio.sleep(1)
            await message.delete()
            return

        # if the message was from an dm, post it in #admin-discussions: Don't do that if bot send an command
        if isinstance(message.channel, discord.channel.DMChannel):
            if not message.author.bot:
                if not text.startswith(COMMAND_PREFIX):
                    admin_discussions_channel = client.get_channel(admin_discussions_channel_id)
                    if message.attachments:
                        attached_files = [discord.File(BytesIO(await attachment.read()),filename=attachment.filename) for attachment in message.attachments]
                        await admin_discussions_channel.send(f"From {message.author.mention}: \n{text}", files=attached_files)
                    else:
                        await admin_discussions_channel.send(f"From {message.author.mention}: \n{text}")
                    await message.author.send("Forwarded your message to staff, you will be contacted shortly 🙃")

        if 'äbidöpfel' in text:
            texts = [   '<:NeriaHeart:671389916277506063> <:NeriaHeart:671389916277506063> <:NeriaHeart:671389916277506063>', 
                        'knows what`s up', 'knows you can do the thing', 'has been voted plushie of the month', 'knows da wey',
                        'yes!', 'does`nt yeet teammtes of the map, be like Häbidöpfel', 'debuggin has proven effective 99.9% of the time (editors note: now 98.9%)',
                        'is cuteness incarnate']
            addition = random.choice(texts)
            await message.channel.send(f'Häbidöpfel {addition}')

        if "welcome" in text.lower() and message.mentions:
            for mention in message.mentions:
                if mention.id == 109022023979667456: #@Neria
                    await message.channel.send(f'Welcome <@109022023979667456>!')
        
        if client.user in message.mentions: #If bot has been tagged
            sentiment = analyzer.polarity_scores(message.clean_content) #{'neg': 0.0, 'neu': 0.436, 'pos': 0.564, 'compound': 0.3802}
            notification = client.get_emoji(751771924866269214) #notification/angerping
            sentimentPositive = client.get_emoji(670369126983794700) #POGGERS
            sentimentNegative = client.get_emoji(670672093263822877) #SadChamp
            await message.add_reaction(notification)
            if sentiment['compound'] > 0.3:
                await message.add_reaction(sentimentPositive)
            if sentiment['compound'] < -0.3:
                await message.add_reaction(sentimentNegative)

        # mute pepe for an hour if he trashes destiny
        if message.author.id == 367385031569702912420:
            if "destiny" in text.lower():
                for insult in ["suck", "bad", "fuck", "shit", "trash"]:
                    if insult in text.lower():
                        # mute pepe and msg him about it
                        await assignRolesToUser([muted_role_id], message.author, message.guild)
                        await message.author.send("Stop trashing on destiny, muted for an hour :)")
                        nick = message.author.nick
                        await message.author.edit(nick="!Pepe the Muted for an Hour")

                        # remove muted role after an hour
                        await asyncio.sleep(60 * 60)
                        await removeRolesFromUser([muted_role_id], message.author, message.guild)
                        await message.author.edit(nick=nick)
                        await message.author.send("Unmuted again :(")
                        return

        # run the command if starts with !
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
                success = insertIntoMessageDB(message.clean_content,message.author.id,message.channel.id,message.id)
        
        if message.author.name == 'EscalatorBot':
            for user in message.mentions:
                member = await message.guild.fetch_member(user.id)
                await member.add_roles(message.guild.get_role(registered_role_id)) #registered role
                await member.remove_roles(message.guild.get_role(not_registered_role_id)) #unregistered role
                await message.channel.send(f'{member.mention} has been marked as Registered')
                await member.send('Registration successful!\nCome say hi in <#670400011519000616>')

                # update user DB
                destinyID = lookupDestinyID(member.id)
                await updateDB(destinyID)

    tasks = []
    @client.event
    async def on_message(message):
        # ignore msg from itself
        if (message.author == client.user):
            return
        asyncio.ensure_future(common_handle_message(message))

    @client.event
    async def on_member_join(member):
        # add @guest and @Not Registered to user
        await assignRolesToUser([guest_role_id], member, member.guild)
        await assignRolesToUser([not_registered_role_id], member, member.guild)

        # add filler roles
        await assignRolesToUser([divider_raider_role_id], member, member.guild)
        await assignRolesToUser([divider_achievement_role_id], member, member.guild)
        await assignRolesToUser([divider_misc_role_id], member, member.guild)

        # inform the user that they should register with the bot
        await member.send(embed=embed_message(
            f'Welcome to Descend {member.name}!',
            f'You can join the destiny clan in **#registration**. \nYou can find our current requirements in the same channel. \n⁣\nWe have a wide variety of roles you can earn, for more information, check out #community-roles. \n⁣\nIf you have any problems / questions, do not hesitate to write **@ElevatorBot** (me) a personal message with your problem / question'
        ))

    @client.event
    async def on_member_remove(member):
        await removeFromClanAfterLeftDiscord(client, member)

    @client.event
    async def on_message_edit(before, after):
        await common_handle_message(after)

    # https://discordpy.readthedocs.io/en/latest/api.html#discord.RawReactionActionEvent
    @client.event
    async def on_raw_reaction_add(payload):
        if not payload.member or payload.member.bot:
            return

        # for checking reactions to the bounties registration page
        if os.path.exists('functions/bounties/channelIDs.pickle'):
            file = getGlobalVar()

            # check if reaction is on the registration page
            if "register_channel_message_id" in file:
                channel_message_id = file["register_channel_message_id"]
                if payload.message_id == channel_message_id:
                    register_channel = discord.utils.get(client.get_all_channels(), guild__id=payload.guild_id, id=file["register_channel"])
                    await registrationMessageReactions(client, payload.member, payload.emoji, register_channel, channel_message_id)

            # check if reaction is on the other game role page
            if "other_game_roles_channel_message_id" in file:
                channel_message_id = file["other_game_roles_channel_message_id"]
                if payload.message_id == channel_message_id:
                    register_channel = discord.utils.get(client.get_all_channels(), guild__id=payload.guild_id, id=file["other_game_roles_channel"])
                    await otherGameRolesMessageReactions(client, payload.member, payload.emoji, register_channel, channel_message_id)

            # check if reaction is on the clan join request page
            if "clan_join_request_channel_message_id" in file:
                channel_message_id = file["clan_join_request_channel_message_id"]
                if payload.message_id == channel_message_id:
                    register_channel = discord.utils.get(client.get_all_channels(), guild__id=payload.guild_id, id=file["clan_join_request_channel"])
                    await clanJoinRequestMessageReactions(client, payload.member, payload.emoji, register_channel, channel_message_id)

            # check if reaction is on the rules page
            if "read_rules_channel_message_id" in file:
                channel_message_id = file["read_rules_channel_message_id"]
                if payload.message_id == channel_message_id:
                    register_channel = discord.utils.get(client.get_all_channels(), guild__id=payload.guild_id, id=file["read_rules_channel"])
                    await readRulesMessageReactions(client, payload.member, payload.emoji, register_channel, channel_message_id)

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
