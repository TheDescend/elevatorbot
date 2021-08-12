# to begin with, start the event loop
# if this is skipped, some imports will fail since they rely on database lookups
# for example GM nightfalls, since they change each season. This allows us to create the hash list dynamically, instead of having to add to it every season
import asyncio
import datetime
import logging
import os
import random
import sys
import threading
import traceback
import urllib
from io import BytesIO

import discord
import pytz
import requests
from aiohttp import web
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_ADDED, EVENT_JOB_REMOVED
from apscheduler.events import EVENT_JOB_MISSED, EVENT_JOB_SUBMITTED
from discord.ext.commands import Bot
from discord_slash import SlashCommand, SlashContext, ComponentContext, ButtonStyle
from discord_slash.utils import manage_components

from database.database import get_connection_pool, \
    select_lfg_datetimes_and_users
from events.base_event import BaseEvent
from functions.clanJoinRequests import removeFromClanAfterLeftDiscord, on_clan_join_request, elevatorRegistration
from functions.destinyPlayer import DestinyPlayer
from functions.formating import embed_message
from functions.lfg import notify_about_lfg_event_start, get_lfg_message
from functions.miscFunctions import update_status, get_scheduler, left_channel, joined_channel
from functions.persistentMessages import check_reaction_for_persistent_message, get_persistent_message_or_channel
from functions.poll import get_poll_object
from functions.roleLookup import assignRolesToUser, removeRolesFromUser
from init_logging import init_logging
from static.config import COMMAND_PREFIX, BOT_TOKEN, ELEVATOR_ADMIN_CLIENT_SECRET
from static.globals import registered_role_id, not_registered_role_id, admin_discussions_channel_id, \
    divider_raider_role_id, divider_achievement_role_id, divider_misc_role_id, muted_role_id, dev_role_id, \
    member_role_id, discord_server_id, join_log_channel_id

# vital, do not delete. Otherwise no events get loaded
from events import *

# to enable the on_member_join and on_member_remove
intents = discord.Intents.default()
intents.members = True

# Set to remember if the bot is already running, since on_ready may be called
# more than once on reconnects
this = sys.modules[__name__]
this.running = False

###############################################################################
from functions.ytdl import play

def aiohttp_server(discord_client):
    def say_hello(request):
        logged_in = {}

        if 'code' in request.query:
            api_url = "https://discord.com/api"
            client_id = 856477753418579978
            client_secret = ELEVATOR_ADMIN_CLIENT_SECRET

            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'authorization_code',
                'code': request.query['code'],
                'redirect_uri': "http://elevatorbot.ch/elevatoradmin"
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            print('requesting token...')
            token_request = requests.post('%s/oauth2/token' % api_url, data=data, headers=headers)
            token_request.raise_for_status()
            oauth_cred = token_request.json()
            access_token = oauth_cred['access_token']

            data_url = "%s/users/@me" % api_url
            print('requesting data...')
            data_request = requests.get(data_url, headers= {'Authorization': f'Bearer {access_token}'})
            user_data = data_request.json()
            user_id = user_data['id']
            user_name = user_data['username']
            user_discriminator = user_data['discriminator']
            logged_in = {
                'user_id': user_id,
                'user_name': user_name,
                'user_discriminator': user_discriminator
            }
            print('logged in!')
        elif 'user_id' in request.query:
            #TODO save in cookie
            logged_in = {
                'user_id': request.query['user_id'],
                'user_name': request.query['user_name'],
                'user_discriminator': request.query['user_discriminator']
            }

        if not "user_id" in logged_in:
            login_ref_url = "https://discord.com/api/oauth2/authorize?client_id=856477753418579978&redirect_uri=http%3A%2F%2Felevatorbot.ch%2Felevatoradmin&response_type=code&scope=identify"
            return web.Response(text=f"login: <a href=\"{login_ref_url}\">auth</a><br/>", content_type='text/html')

        connections = discord_client.voice_clients
        if not 'guild' in request.query:
            login_json = urllib.parse.urlencode(logged_in)
            return web.Response(text=f"""
            Select guild:
            <script>
                function setGuild() {{
                    location.replace("elevatoradmin?guild=669293365900214293&{login_json}");
                }}
                </script>
            <button type="button" onclick="setGuild()">Descend</button>
            """, content_type='text/html')
        
        guild = discord_client.get_guild(int(request.query['guild']))
        discord_member = guild.get_member(int(logged_in['user_id']))

        if not discord_member:
            print(f'{logged_in["user_name"]} not in guild')
            return web.Response(text="Member not in guild"
                r"""<script>window.history.pushState({page: 1}, "Login Failed", "/elevatoradmin");</script>"""
                , content_type='text/html')

        member_roles = [role.name for role in discord_member.roles]
        good_roles = ['Moderator', 'Developer', 'Admin']
        if not any([role in good_roles for role in member_roles]):
            return web.Response(text="You don't seem to have permission to play music")

        if 'join' in request.query and 'req' in request.query:
            voice_chat = guild.get_channel(int(request.query['join']))
            print(f"{logged_in['user_name']}#{logged_in['user_discriminator']} joined bot to {request.query['join']}")

            active = list(filter(lambda voice_client: voice_client.guild.id == guild.id and voice_client.is_connected(), connections))
            if len(active) == 1:
                move_task = loop.create_task(active[0].move_to(voice_chat))
                if active[0].is_playing():
                    active[0].stop()
                loop.create_task(play(urllib.parse.unquote(request.query['req']), discord_client, move_task, voice_client=active[0]))
            else:
                print(f'joining {voice_chat.name}')
                connection_task = loop.create_task(voice_chat.connect(timeout=5, reconnect=True))
                if request.query['req'] != '':
                    print(f"starting to play {request.query['req']}")
                    loop.create_task(play(urllib.parse.unquote(request.query['req']), discord_client, connection_task))
            return web.Response(text=f"Playing {request.query['req']}")
        elif 'disconnect' in request.query:
            active = list(filter(lambda voice_client: voice_client.guild.id == guild.id and voice_client.is_connected(), connections))
            if len(active) == 1:
                loop.create_task(active[0].disconnect())
            return web.Response(text='Disconnected')
        elif 'stop' in request.query:
            active = list(filter(lambda voice_client: voice_client.guild.id == guild.id and voice_client.is_connected(), connections))
            if len(active) == 1:
                active[0].stop()
            return web.Response(text='Stopped')

        if guild := discord_client.get_guild(669293365900214293):
            return web.Response(text= 
                f"Logged in as {logged_in['user_name']}#{logged_in['user_discriminator']}<br/>"
                r"""<script>window.history.pushState({page: 1}, "MusicBot Admin", "/elevatoradmin");</script>"""
                "Songname:<input id='songname' type='text'></input> <br/> Click Channel to join/start playing <br/> (might take up to 10s, depending on song size) <br/><br/>" + \
                "<br/>".join(f"""
                        <button type="button" onclick="join{vc.id}()">{vc.name}</button> {', '.join([m.name for m in vc.members])}
                        <script>
                        function join{vc.id}() {{
                            const xhttp = new XMLHttpRequest();
                            const song_req = encodeURI(document.getElementById("songname").value);
                            console.log(song_req);
                            xhttp.onreadystatechange = function() {{
                                if (this.readyState == 4 && this.status == 200) {{
                                    document.getElementById("news").innerHTML = this.responseText;
                                }}
                            }};
                            xhttp.open("GET", "/elevatoradmin?guild={vc.guild.id}&join={vc.id}&req=" + song_req + "&{urllib.parse.urlencode(logged_in)}");
                            xhttp.send();
                        }}
                        </script>
                """ for vc in guild.voice_channels) + \
                f"""
                <br/><br/>
                <button type="button" onclick="stop()">Stop playing</button>
                <script>
                        function stop() {{
                            const xhttp = new XMLHttpRequest();
                            xhttp.onreadystatechange = function() {{
                                if (this.readyState == 4 && this.status == 200) {{
                                    document.getElementById("news").innerHTML = this.responseText;
                                }}
                            }};
                            const song_req = encodeURI(document.getElementById("songname").value);
                            xhttp.open("GET", "/elevatoradmin?stop=1&guild={guild.id}" + "&{urllib.parse.urlencode(logged_in)}");
                            xhttp.send();
                        }}
                </script>
                <button type="button" onclick="disconnect()">Disconnect</button>
                <script>
                        function disconnect() {{
                            const xhttp = new XMLHttpRequest();
                            xhttp.onreadystatechange = function() {{
                                if (this.readyState == 4 && this.status == 200) {{
                                    document.getElementById("news").innerHTML = this.responseText;
                                }}
                            }};
                            const song_req = encodeURI(document.getElementById("songname").value);
                            xhttp.open("GET", "/elevatoradmin?disconnect=1&guild={guild.id}" + "&{urllib.parse.urlencode(logged_in)}");
                            xhttp.send();
                        }}
                </script>
                <br/><br/>
                <div id="news"></div>
            """, content_type='text/html')
        return web.Response(text='500')
    loop = asyncio.get_event_loop()

    app = web.Application()
    app.add_routes([web.get('/', say_hello)])
    runner = web.AppRunner(app)
    return runner


def run_server(runner):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    print(f'webserver running {site}')
    loop.run_until_complete(site.start())
    loop.run_forever()


###############################################################################


async def launch_event_loops(client):
    await get_connection_pool()
    print("Made sure we are connected to the DB")

    # Scheduler that will be used to manage events
    sched = get_scheduler()

    # add listeners to catch and format errors also to log
    def event_added(sched_event):
        job_name = sched.get_job(sched_event.job_id)

        # log the execution
        logger = logging.getLogger('events')
        logger.info("Event '%s' with ID '%s' has been added", job_name, sched_event.job_id)

    sched.add_listener(event_added, EVENT_JOB_ADDED)

    def event_removed(sched_event):
        # log the execution
        logger = logging.getLogger('events')
        logger.info("Event with ID '%s' has been removed", sched_event.job_id)

    sched.add_listener(event_removed, EVENT_JOB_REMOVED)

    def event_submitted(sched_event):
        job_name = sched.get_job(sched_event.job_id)
        print(f"Running '{job_name}'")

    sched.add_listener(event_submitted, EVENT_JOB_SUBMITTED)

    def event_executed(sched_event):
        job_name = sched.get_job(sched_event.job_id)

        # log the execution
        logger = logging.getLogger('events')
        logger.info("Event '%s' successfully run", job_name)

    sched.add_listener(event_executed, EVENT_JOB_EXECUTED)

    def event_missed(sched_event):
        job_name = sched.get_job(sched_event.job_id)

        # log the execution
        logger = logging.getLogger('events')
        logger.warning("Event '%s' missed", job_name)

    sched.add_listener(event_missed, EVENT_JOB_MISSED)

    def event_error(sched_event):
        job_name = sched.get_job(sched_event.job_id)

        # log the execution
        logger = logging.getLogger('events')
        logger.error(
            "Event '%s' failed - Error '%s' - Traceback: \n%s",
            job_name, sched_event.exception, sched_event.traceback
        )

    sched.add_listener(event_error, EVENT_JOB_ERROR)

    print("Loading events...")
    for ev in BaseEvent.__subclasses__():
        event = ev()

        # check the type of job and schedule acordingly
        if event.scheduler_type == "interval":
            sched.add_job(event.run, 'interval', (client,), minutes=event.interval_minutes, jitter=60)
        elif event.scheduler_type == "cron":
            sched.add_job(event.run, 'cron', (client,), day_of_week=event.dow_day_of_week, hour=event.dow_hour, minute=event.dow_minute, timezone=pytz.utc)
        elif event.scheduler_type == "date":
            sched.add_job(event.run, 'date', (client,), run_date=event.run_date)
        else:
            print(f"Failed to load event {event}")
    jobs = sched.get_jobs()
    print(f"{len(jobs)} events loaded")

    # load the lfg events
    lfg_events = await select_lfg_datetimes_and_users()
    for lfg_event in lfg_events:
        guild = client.get_guild(lfg_event["guild_id"])
        if guild:
            timedelta = datetime.timedelta(minutes=10)
            sched.add_job(notify_about_lfg_event_start, 'date', (client, guild, lfg_event["id"], timedelta),
                          run_date=lfg_event["start_time"] - timedelta, id=str(lfg_event["id"]))
    print(f"{len(sched.get_jobs()) - len(jobs)} LFG events loaded")

    print("Startup complete!")

    # Set the playing status
    await update_status(client)


def main():
    """the main method"""

    # Initialize logging
    init_logging()

    # Initialize the client
    print("Starting up...")
    client = Bot('!', intents=intents)

    # start webserver
    if ELEVATOR_ADMIN_CLIENT_SECRET:
        webserver_thread = threading.Thread(target=run_server, args=(aiohttp_server(client),))
        webserver_thread.start()

    # enable slash commands and send them to the discord API
    slash = SlashCommand(client, sync_commands=True)

    # load slash command cogs
    # to do that, loop through the files and import all classes and commands
    print("Loading commands...")
    slash_dir = "slash_commands"
    for file in os.listdir(slash_dir):
        if file.endswith(".py"):
            file = file.removesuffix(".py")
            extension = f"{slash_dir}.{file}"
            client.load_extension(extension)

    # pylint: disable=no-member
    print(f"{len(client.slash.commands)} commands loaded")

    # Define event handlers for the client
    # on_ready may be called multiple times in the event of a reconnect,
    @client.event
    async def on_ready():
        if this.running:
            return
        this.running = True
        print("Logged in")

        # run further launch event loops
        await launch_event_loops(client)

    # The message handler for both new message and edits
    @client.event
    async def common_handle_message(message):
        text = message.content

        # if the message was from an dm, post it in #admin-discussions: Don't do that if bot send an command
        if isinstance(message.channel, discord.channel.DMChannel):
            if not message.author.bot:
                if not text.startswith(COMMAND_PREFIX):
                    admin_discussions_channel = client.get_channel(admin_discussions_channel_id)
                    if message.attachments:
                        attached_files = [discord.File(BytesIO(await attachment.read()), filename=attachment.filename)
                                          for attachment in message.attachments]
                        await admin_discussions_channel.send(f"From {message.author.mention}: \n{text}",
                                                             files=attached_files)
                    else:
                        await admin_discussions_channel.send(f"From {message.author.mention}: \n{text}")
                    await message.author.send("Forwarded your message to staff, you will be contacted shortly 🙃")

        if 'äbidöpfel' in text:
            texts = [
                '<:NeriaHeart:671389916277506063> <:NeriaHeart:671389916277506063> <:NeriaHeart:671389916277506063>',
                'knows what`s up', 'knows you can do the thing', 'has been voted plushie of the month', 'knows da wey',
                'yes!', 'does`nt yeet teammtes of the map, be like Häbidöpfel',
                'debuggin has proven effective 99.9% of the time (editors note: now 98.9%)',
                'is cuteness incarnate']
            addition = random.choice(texts)
            await message.channel.send(f'Häbidöpfel {addition}')

        if "welcome" in text.lower() and message.mentions:
            for mention in message.mentions:
                neria_id = 109022023979667456
                if mention.id == neria_id:
                    welcome_choice = [
                        "Welcome",
                        "I mirëpritur",
                        "Dobrodošli",
                        "Vitejte",
                        "Welkom",
                        "Tere tulemast",
                        "Tervetuloa",
                        "Bienvenue",
                        "Herzlich willkommen",
                        "Üdvözöljük",
                        "Velkominn",
                        "Fáilte",
                        "Benvenuta",
                        "Velkommen",
                        "Witamy",
                        "Bine ați venit (this is spelled correctly thanks to <@171371726444167168>)",
                        "Bienvenidas",
                        "Välkommen",
                        "Croeso",
                        "Yeeeeeeeeeeeeeeeeeeeeeeeeeeeeehaw",
                    ]
                    await message.channel.send(f'{random.choice(welcome_choice)} <@{neria_id}>!')

        if client.user in message.mentions:  # If bot has been tagged
            notification = client.get_emoji(751771924866269214)  # notification/angerping
            # sentimentPositive = client.get_emoji(670369126983794700) #POGGERS
            # sentimentNegative = client.get_emoji(670672093263822877) #SadChamp
            await message.add_reaction(notification)

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

        if message.author.name == 'EscalatorBot':
            for user in message.mentions:
                member = await message.guild.fetch_member(user.id)
                await member.add_roles(message.guild.get_role(registered_role_id))  # registered role
                await member.remove_roles(message.guild.get_role(not_registered_role_id))  # unregistered role
                await message.channel.send(f'{member.mention} has been marked as Registered')
                await member.send('Registration successful!\nCome say hi in <#670400011519000616>')

                # update user DB
                destiny_player = await DestinyPlayer.from_discord_id(member.id)
                await destiny_player.update_activity_db()

    @client.event
    async def on_message(message):
        # ignore msg from itself
        if (message.author == client.user):
            return
        asyncio.ensure_future(common_handle_message(message))

    @client.event
    async def on_member_join(member):
        # inform the user that they should register with the bot
        await member.send(embed=embed_message(
            f'Welcome to Descend {member.name}!',
            'You can join the destiny clan in **#registration**. \nYou can find our current requirements in the same channel. \n⁣\nWe have a wide variety of roles you can earn, for more information, check out #community-roles. \n⁣\nIf you have any problems / questions, do not hesitate to write **@ElevatorBot** (me) a personal message with your problem / question'
        ))

    @client.event
    async def on_member_remove(member: discord.Member):
        # send a message in the join log channel if the server is descend
        if member.guild.id == discord_server_id:
            embed = embed_message(
                "Member Left the Server",
                f"{member.mention} has left the server"
            )
            embed.add_field(name="Display Name", value=member.display_name)
            embed.add_field(name="Name", value=member.name)
            embed.add_field(name="Discord ID", value=member.id)
            await member.guild.get_channel(join_log_channel_id).send(embed=embed)

        await removeFromClanAfterLeftDiscord(client, member)

    @client.event
    async def on_message_edit(before, after):
        await common_handle_message(after)

    # https://discordpy.readthedocs.io/en/latest/api.html#discord.RawReactionActionEvent
    @client.event
    async def on_raw_reaction_add(payload):
        if not payload.member or payload.member.bot:
            return

        # check if reaction is on a persistent message
        await check_reaction_for_persistent_message(client, payload)

    @client.event
    async def on_voice_state_update(member, before, after):
        guild = member.guild
        lfg_voice_category_channel = await get_persistent_message_or_channel(client, "lfgVoiceCategory", guild.id)

        if before.channel is None:
            # print(f'{member.name} joined VC {after.channel.name}')
            await joined_channel(client, member, after.channel)
            return

        if after.channel is None:
            # print(f'{member.name} left VC {before.channel.name}')
            await left_channel(client, member, before.channel, after.channel, lfg_voice_category_channel)
            return

        if before.channel != after.channel:
            # print(f'{member.name} changed VC from {before.channel.name} to {after.channel.name}')
            await joined_channel(client, member, after.channel)
            await left_channel(client, member, before.channel, after.channel, lfg_voice_category_channel)
            return

    @client.event
    async def on_member_update(before, after):
        """ Add member role after Role Screening """

        if before.bot or after.bot:
            return
        if before.pending and not after.pending:
            member = client.get_guild(before.guild.id).get_member(before.id)

            # add @member
            await assignRolesToUser([member_role_id], member, member.guild)

            # add @Not Registered to user
            await assignRolesToUser([not_registered_role_id], member, member.guild)

            # add filler roles
            await assignRolesToUser([divider_raider_role_id], member, member.guild)
            await assignRolesToUser([divider_achievement_role_id], member, member.guild)
            await assignRolesToUser([divider_misc_role_id], member, member.guild)

    @client.event
    async def on_slash_command(ctx: SlashContext):
        """ Gets triggered every slash command """

        # print the command
        print(f"{ctx.author.display_name} used '/{ctx.name}' with kwargs '{ctx.kwargs}'")

        # log the command
        logger = logging.getLogger('slash_commands')
        logger.info(
            f"InteractionID '{ctx.interaction_id}' - User '{ctx.author.name}' with discordID '{ctx.author.id}' executed '/{ctx.name}' with kwargs '{ctx.kwargs}' in guildID '{ctx.guild.id}', channelID '{ctx.channel.id}'")

    @client.event
    async def on_slash_command_error(ctx: SlashContext, error: Exception):
        """ Gets triggered on slash errors """

        await ctx.send(embed=embed_message(
            "Error",
            f"Sorry, something went wrong \nPlease contact a {ctx.guild.get_role(dev_role_id)}",
            error
        ))

        # log the error
        logger = logging.getLogger('slash_commands')
        logger.exception(
            f"InteractionID '{ctx.interaction_id}' - Error {error} - Traceback: \n{''.join(traceback.format_tb(error.__traceback__))}")

        # raising error again to making deving easier
        raise error

    # handle registrations
    @slash.component_callback()
    async def registration(ctx: ComponentContext):
        await elevatorRegistration(ctx.author)

        await ctx.send(hidden=True, embed=embed_message(
            f"Thanks for Registering",
            f"I sent you a DM with the next steps!"
        ))

    # handle other game roles
    @slash.component_callback()
    async def other_game_roles(ctx: ComponentContext):
        user_role_ids = [role.id for role in ctx.author.roles]

        added = []
        removed = []

        # loop through the roles the user want (to loose)
        for role in ctx.selected_options:
            role_name, role_id = role.split("|")
            role_id = int(role_id)

            # add role
            if role_id not in user_role_ids:
                await assignRolesToUser([role_id], ctx.author, ctx.guild)
                added.append(role_name)

            # remove role
            else:
                await removeRolesFromUser([role_id], ctx.author, ctx.guild)
                removed.append(role_name)

        # send message to user
        embed = embed_message(
            f"Role Update",
        )
        if added:
            embed.add_field(name="Roles Added", value="\n".join(added), inline=True)
        if removed:
            embed.add_field(name="Roles Removed", value="\n".join(removed), inline=True)

        await ctx.send(hidden=True, embed=embed)

    # handle increment button
    @slash.component_callback()
    async def increment_button(ctx: ComponentContext):
        components = [
            manage_components.create_actionrow(
                manage_components.create_button(
                    custom_id="increment_button",
                    style=ButtonStyle.blue,
                    label=str(int(ctx.component["label"]) + 1)
                ),
            ),
        ]
        embed = ctx.origin_message.embeds[0]
        embed.description = f"Last used by {ctx.author.mention} <:PeepoZoom:670369608498151456>"

        if int(ctx.component["label"]) == 69420:
            await ctx.send(hidden=True, content=f"Sorry, the game has been won and is over!")
        else:
            await ctx.edit_origin(components=components, embed=embed)


    # handle lfg messages
    @slash.component_callback()
    async def lfg_join(ctx: ComponentContext):
        # get the lfg message
        lfg_message = await get_lfg_message(client=ctx.bot, lfg_message_id=ctx.origin_message.id, guild=ctx.guild)
        if not lfg_message:
            return

        res = await lfg_message.add_member(member=ctx.guild.get_member(ctx.author.id), ctx=ctx)
        if not res:
            await ctx.send(hidden=True, embed=embed_message(
                "Error",
                "You could not be added to the event\nThis is either because you are already in the event, the event is full, or the creator has blacklisted you from their events"
            ))

    @slash.component_callback()
    async def lfg_leave(ctx: ComponentContext):
        # get the lfg message
        lfg_message = await get_lfg_message(client=ctx.bot, lfg_message_id=ctx.origin_message.id, guild=ctx.guild)
        if not lfg_message:
            return

        res = await lfg_message.remove_member(member=ctx.guild.get_member(ctx.author.id), ctx=ctx)
        if not res:
            await ctx.send(hidden=True, embed=embed_message(
                "Error",
                "You could not be removed from the event\nThis is because you are neither in the main nor in the backup roster"
            ))

    @slash.component_callback()
    async def lfg_backup(ctx: ComponentContext):
        # get the lfg message
        lfg_message = await get_lfg_message(client=ctx.bot, lfg_message_id=ctx.origin_message.id, guild=ctx.guild)
        if not lfg_message:
            return

        res = await lfg_message.add_backup(member=ctx.guild.get_member(ctx.author.id), ctx=ctx)
        if not res:
            await ctx.send(hidden=True, embed=embed_message(
                "Error",
                "You could not be added as a backup to the event\nThis is either because you are already in the backup roster, or the creator has blacklisted you from their events"
            ))

    # handle clan join requests
    @slash.component_callback()
    async def clan_join_request(ctx: ComponentContext):
        await on_clan_join_request(ctx)

    # handle poll selects
    @slash.component_callback()
    async def poll(ctx: ComponentContext):
        poll = await get_poll_object(
            guild=ctx.guild,
            poll_message_id=ctx.origin_message.id
        )
        await poll.add_user(
            select_ctx=ctx,
            member=ctx.author,
            option=ctx.selected_options[0]
        )


    # Finally, set the bot running
    client.run(BOT_TOKEN)


###############################################################################


if __name__ == "__main__":
    # p = Process(target=start_server)
    # p.start()
    # print('server started')

    main()

    # p.join()
