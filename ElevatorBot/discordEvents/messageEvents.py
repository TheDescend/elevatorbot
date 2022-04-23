import asyncio
import datetime
import os
import pathlib
import random
import re

import aiohttp
import github
import gtts
from dateparser.search import search_dates
from dis_snek import AutoArchiveDuration, ChannelTypes, ThreadChannel, ThreadList, Timestamp, TimestampStyles
from dis_snek.api.events import MessageCreate, MessageDelete, MessageUpdate
from dis_snek.api.voice.audio import AudioVolume, YTDLAudio

from ElevatorBot.core.misc.aprilFools import play_joke
from ElevatorBot.core.misc.github import github_manager
from ElevatorBot.core.misc.timestamps import get_timestamp_embed
from ElevatorBot.misc.cache import reply_cache
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.github import get_github_repo
from ElevatorBot.static.descendOnlyIds import descend_channels
from ElevatorBot.static.emojis import custom_emojis
from Shared.functions.readSettingsFile import get_setting


async def on_message_delete(event: MessageDelete):
    """Triggers when a message gets deleted"""

    # ignore bot messages
    if not event.message.author.bot:
        # check if the deleted message was part of the conversation with a member and admins
        if event.message.id in reply_cache.thread_message_id_to_user_message:
            message = reply_cache.thread_message_id_to_user_message[event.message.id]
            await message.delete()
            reply_cache.thread_message_id_to_user_message.pop(message.id)

        elif event.message.id in reply_cache.user_message_id_to_thread_message:
            message = reply_cache.user_message_id_to_thread_message[event.message.id]
            await message.delete()
            reply_cache.user_message_id_to_thread_message.pop(message.id)


async def on_message_update(event: MessageUpdate):
    """Triggers when a message gets edited"""

    if event.before != event.after and event.after:
        # run the message create checks
        await on_message_create(event=MessageCreate(bot=event.bot, message=event.after), edit_mode=True)


async def on_message_create(event: MessageCreate, edit_mode: bool = False):
    """Triggers when a message gets send"""

    message = event.message

    # ignore bot messages
    if not message.author.bot:
        # =========================================================================
        # handle thread messages
        if isinstance(message.channel, ThreadChannel):
            thread = message.channel

            # only do this for descend
            if message.guild == descend_channels.guild:
                # check that the message starts with a @ElevatorBot mention and remove that
                # noinspection PyProtectedMember
                if event.bot.user.id in message._mention_ids:
                    # remove the mention with a regex
                    content = re.sub(f"<@!*&*{event.bot.user.id}+>", "", message.content, 1).strip()

                    send = False

                    # check if message is in cache
                    if thread.id in reply_cache.thread_to_user:
                        send = True

                    # look if it follows the naming scheme and is in the correct channel
                    elif thread.parent_channel.id in [
                        descend_channels.admin_channel.id,
                        descend_channels.bot_dev_channel.id,
                    ] and thread.name.startswith("Message from"):
                        linked_user_id = thread.name.split("|")[1].strip()
                        linked_user = await event.bot.fetch_user(linked_user_id)

                        if linked_user:
                            # save in cache
                            reply_cache.user_to_thread.update({linked_user.id: thread})
                            reply_cache.thread_to_user.update({thread.id: linked_user.id})

                            send = True

                    if send:
                        # alright, lets send that to the linked member
                        linked_user = await event.bot.fetch_user(reply_cache.thread_to_user[thread.id])

                        # add the urls to the message
                        attached_files = [attachment.url for attachment in message.attachments]
                        if attached_files:
                            attached_files.insert(0, "⁣\n__**Attachments**__")
                            if message.content:
                                attached_files.insert(0, content)
                            content = "\n".join(attached_files)

                        # send the message
                        if not edit_mode:
                            user_message = await linked_user.send(content=content)
                            reply_cache.thread_message_id_to_user_message.update({message.id: user_message})

                        # edit the message
                        else:
                            user_message = (
                                reply_cache.thread_message_id_to_user_message[message.id]
                                if message.id in reply_cache.thread_message_id_to_user_message
                                else None
                            )
                            if user_message:
                                await user_message.edit(content=content)
                            else:
                                user_message = await linked_user.send(content=content)
                                reply_cache.thread_message_id_to_user_message.update({message.id: user_message})

                        # react to the message to signal the OK
                        await message.add_reaction(custom_emojis.descend_logo)

        # =========================================================================
        # handle dm messages
        elif not message.guild:
            # reads a DM message and sends to Descend if the author is in the Descend Server
            mutual_guilds = message.author.mutual_guilds
            if mutual_guilds:
                # check is author is in descend. Checking COMMAND_GUILD_SCOPE for that, since that already has the id and doesn't break testing
                allowed_guilds = [
                    await event.bot.fetch_guild(guild_id) for guild_id in get_setting("COMMAND_GUILD_SCOPE")
                ]
                mutual_allowed_guilds = [guild for guild in allowed_guilds if guild in mutual_guilds]

                if mutual_allowed_guilds:
                    thread_name = f"Message from {message.author.username} | {message.author.id}"

                    # we just need to get the url, no need to re-upload
                    attached_files = [attachment.url for attachment in message.attachments]

                    # before we send a message, check the cache to see if we already made a thread for that user
                    if message.author.id in reply_cache.user_to_thread:
                        thread = reply_cache.user_to_thread[message.author.id]

                    else:
                        channel_threads: ThreadList = await descend_channels.admin_channel.fetch_all_threads()

                        # maybe a thread does exist, but is not cached since we restarted
                        threads = [thread for thread in channel_threads.threads if thread.name == thread_name]

                        if threads:
                            # only one entry
                            thread = threads[0]

                        else:
                            # create a thread
                            thread = await descend_channels.admin_channel.create_thread_without_message(
                                name=thread_name,
                                thread_type=ChannelTypes.GUILD_PUBLIC_THREAD,
                                auto_archive_duration=AutoArchiveDuration.ONE_HOUR,
                                reason="Received DM",
                            )

                            # ping all users
                            pings = await thread.send(
                                " ".join([member.mention for member in thread.parent_channel.humans])
                            )
                            await pings.delete()

                            # first message in thread
                            await thread.send(
                                embeds=embed_message(
                                    "Inquiry",
                                    f"Any message you send here that starts with `@ElevatorBot` is relayed to them (not including the mention of course)\nAlternatively, you can reply to the message\nI will react with {custom_emojis.descend_logo} if I conveyed the message successfully\n⁣\nAll messages from me are directly forwarded from {message.author.mention}",
                                    member=message.author,
                                )
                            )

                            # send author a message to let them know that we got the msg
                            await message.author.send(
                                embeds=embed_message(
                                    "Inquiry",
                                    "I forwarded your message to staff, you will be contacted shortly 🙃",
                                    member=message.author,
                                )
                            )

                        # save in cache
                        reply_cache.user_to_thread.update({message.author.id: thread})
                        reply_cache.thread_to_user.update({thread.id: message.author.id})

                    # send the message
                    if not edit_mode:
                        content = message.content

                        # add the urls to the message
                        if attached_files:
                            attached_files.insert(0, "⁣\n__**Attachments**__")
                            if message.content:
                                attached_files.insert(0, content)
                            content = "\n".join(attached_files)

                        thread_message = await thread.send(content=content)
                        reply_cache.user_message_id_to_thread_message.update({message.id: thread_message})

                    # edit the message
                    else:
                        thread_message = (
                            reply_cache.user_message_id_to_thread_message[message.id]
                            if message.id in reply_cache.user_message_id_to_thread_message
                            else None
                        )
                        if thread_message:
                            await thread_message.edit(content=message.content)
                        else:
                            thread_message = await thread.send(content=message.content)
                            reply_cache.user_message_id_to_thread_message.update({message.id: thread_message})

        # =========================================================================
        # handle guild messages
        else:
            # descend only stuff
            if message.guild == descend_channels.guild:
                # whatever this is
                if "äbidöpfel" in message.content.lower():
                    texts = [
                        "<:NeriaHeart:671389916277506063> <:NeriaHeart:671389916277506063> <:NeriaHeart:671389916277506063>",
                        "knows what`s up",
                        "knows you can do the thing",
                        "has been voted plushie of the month",
                        "knows da wey",
                        "yes!",
                        "does`nt yeet teammtes of the map, be like Häbidöpfel",
                        "debuggin has proven effective 99.9% of the time (editors note: now 98.9%)",
                        "is cuteness incarnate",
                    ]
                    addition = random.choice(texts)
                    await message.channel.send(f"Häbidöpfel {addition}")

                # =========================================================================
                # neria welcome message
                if "welcome" in message.content.lower():
                    # nerias id
                    # todo move over to new mention property I will make
                    if 109022023979667456 in message._mention_ids:
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
                        await message.channel.send(f"{random.choice(welcome_choice)} <@{neria_id}>!")

                # =========================================================================
                # be annoyed if getting pinged
                if event.bot.user.id in message._mention_ids:
                    await message.add_reaction(custom_emojis.ping)

                # =========================================================================
                # make deving with github easier
                message = event.message
                in_data = message.content.lower()

                try:
                    if "github.com/" in in_data and "#l" in in_data:
                        return await github_manager.send_snippet(message)
                    elif data := re.search(r"(?:\s|^)#(\d{1,3})(?:\s|$)", in_data):
                        # only send issues and prs in the dev channels
                        if (
                            event.message.channel == descend_channels.bot_dev_channel
                            or event.message.channel == descend_channels.admin_channel
                        ):
                            issue = await github_manager.get_issue(await get_github_repo(), int(data.group(1)))
                            if not issue:
                                return

                            if issue.pull_request:
                                pr = await github_manager.get_pull(await get_github_repo(), int(data.group(1)))
                                return await github_manager.send_pr(message=message, pr=pr)
                            return await github_manager.send_issue(message, issue)
                except (github.UnknownObjectException, github.GithubException):
                    pass

                # =========================================================================
                # parse datetimes
                if embed := await get_timestamp_embed(search_string=message.content.upper(), parse_relative=False):
                    await message.reply(embeds=embed)

                # =========================================================================
                # april fools

                if event.bot.user.id in message._mention_ids and "joke" in in_data:
                    voice_state = event.message.author.voice
                    run = True

                    # user not in voice
                    if not voice_state:
                        await message.reply("You are not in a voice channel, how am I supposed to tell you a joke???")

                    else:
                        bot_voice_state = event.bot.get_bot_voice_state(guild_id=voice_state.guild.id)

                        # bot not in voice
                        if bot_voice_state and bot_voice_state.connected:
                            await message.reply("I'm busy telling a joke, try again in a bit")
                            run = False

                        else:
                            # connect to the authors voice channel
                            bot_voice_state = await voice_state.channel.connect()

                        if run:
                            await play_joke(bot_voice_state=bot_voice_state, message=message)

            # =========================================================================
            # valid for all guilds
