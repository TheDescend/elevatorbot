import random

from dis_snek.models import AutoArchiveDuration, ChannelTypes, ThreadList
from dis_snek.models.events import MessageCreate, MessageDelete, MessageUpdate

from ElevatorBot.misc.cache import reply_cache
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.descendOnlyIds import descend_channels
from ElevatorBot.static.emojis import custom_emojis
from settings import COMMAND_GUILD_SCOPE


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

    if event.before != event.after:
        # run the message create checks
        await on_message_create(event=MessageCreate(bot=event.bot, message=event.after), edit_mode=True)


async def on_message_create(event: MessageCreate, edit_mode: bool = False):
    """Triggers when a message gets send"""

    message = event.message

    # ignore bot messages
    if not message.author.bot:
        # =========================================================================
        # handle thread messages
        if message.thread:
            thread = message.thread

            # only do this for descend
            if message.guild == descend_channels.guild:
                send = False

                # check if message is in cache
                if thread in reply_cache.thread_to_user:
                    send = True

                # look if it follows the naming scheme and is in the correct channel
                elif (
                    thread.channel.id
                    in [
                        descend_channels.admin_channel.id,
                        descend_channels.bot_dev_channel.id,
                    ]
                    and thread.name.startswith("Message from")
                ):
                    linked_user_id = thread.name.split("|")[1]
                    linked_user = await event.bot.get_user(linked_user_id)

                    if linked_user:
                        # save in cache
                        reply_cache.user_to_thread.update({linked_user.id: thread})
                        reply_cache.thread_to_user.update({thread: linked_user.id})

                        send = True

                if send:
                    # check that the message starts with a @ElevatorBot mention and remove that
                    content = message.content
                    if content.startswith(event.bot.user.mention):
                        content.removeprefix(event.bot.user.mention)

                        # alright, lets send that to the linked member
                        linked_user = await event.bot.get_user(reply_cache.thread_to_user[thread])

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

                        # also send images
                        for url in [attachment.url for attachment in message.attachments]:
                            await linked_user.send(content=url)

                        # react to the message to signal the OK
                        await message.add_reaction(custom_emojis.descend_logo)

        # =========================================================================
        # handle dm messages
        elif not message.guild:
            # reads a DM message and sends to Descend if the author is in the Descend Server
            mutual_guilds = message.author.guilds
            if mutual_guilds:
                # check is author is in descend. Checking COMMAND_GUILD_SCOPE for that, since that already has the id and doesn't break testing
                allowed_guilds = [await event.bot.get_guild(guild_id) for guild_id in COMMAND_GUILD_SCOPE]
                mutual_allowed_guilds = [g for g in allowed_guilds if g.id in mutual_guilds]

                if mutual_allowed_guilds:
                    thread_name = (
                        f"Message from {message.author.username}_{message.author.discriminator}|{message.author.id}"
                    )

                    # we just need to get the url, no need to re-upload
                    attached_files = [attachment.url for attachment in message.attachments]

                    # before we send a message, check the cache to see if we already made a thread for that user
                    if message.author.id in reply_cache.user_to_thread:
                        thread = reply_cache.user_to_thread[message.author.id]

                    else:
                        channel_threads: ThreadList = await descend_channels.admin_channel.get_all_threads()

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

                            # first message in thread
                            await thread.send(
                                embeds=embed_message(
                                    f"{message.author.display_name}'s Inquiry",
                                    f"Any message you send here that starts with `@ElevatorBot` is relayed to them (not including the mention of course)\nI will react with {custom_emojis.descend_logo} if I conveyed the message successfully",
                                )
                            )

                            # send author a message to let them know that we got the msg
                            await message.author.send(
                                embeds=embed_message(
                                    "Your Inquiry", "I forwarded your message to staff, you will be contacted shortly 🙃"
                                )
                            )

                        # save in cache
                        reply_cache.user_to_thread.update({message.author.id: thread})
                        reply_cache.thread_to_user.update({thread: message.author.id})

                    # send the message
                    if not edit_mode:
                        thread_message = await thread.send(content=message.content)
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

                    for url in attached_files:
                        await thread.send(content=url)

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
                if "welcome" in message.content.lower() and message.mentions:
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
                            await message.channel.send(f"{random.choice(welcome_choice)} <@{neria_id}>!")

            # =========================================================================
            # valid for all guilds

            # be annoyed if getting pinged
            if event.bot.user in message.mentions:
                await message.add_reaction(custom_emojis.ping_sock)
