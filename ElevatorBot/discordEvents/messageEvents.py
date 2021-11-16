from dis_snek.client import Snake
from dis_snek.models import (
    AutoArchiveDuration,
    ChannelTypes,
    GuildText,
    Message,
    ThreadChannel,
)

from ElevatorBot.misc.cache import reply_cache
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.descendOnlyIds import (
    bot_dev_channel_id,
    descend_admin_channel_id,
)
from settings import COMMAND_GUILD_SCOPE


async def on_message_delete(message: Message):
    """Triggers when a message gets deleted"""

    # todo
    pass


async def on_message_edit(before: Message, after: Message):
    """Triggers when a message gets edited"""

    # todo
    pass


async def on_message_create(message: Message):
    """Triggers when a message gets send"""

    # ignore bot messages
    if not message.author.bot:
        client = message._client

        # handle thread messages
        if message.thread:
            thread = message.thread

            # only do this for descend
            if message.guild.id in COMMAND_GUILD_SCOPE:
                send = False

                # check if message is in cache
                if thread in reply_cache.thread_to_user:
                    send = True

                # look if it follows the naming scheme and is in the correct channel
                elif thread.channel.id in [descend_admin_channel_id, bot_dev_channel_id] and thread.name.startswith(
                    "Message from"
                ):
                    linked_user_id = thread.name.split("|")[1]
                    linked_user = await client.get_user(linked_user_id)

                    if not linked_user:
                        return

                    # save in cache
                    reply_cache.user_to_thread.update({linked_user.id: thread})
                    reply_cache.thread_to_user.update({thread: linked_user.id})

                    send = True

                if send:
                    # alright, lets send that to the linked member
                    linked_user = await client.get_user(reply_cache.thread_to_user[thread])
                    await linked_user.send(content=message.content)

                    # also send images
                    for url in [attachment.url for attachment in message.attachments]:
                        await linked_user.send(content=url)

        # handle dm messages
        elif not message.guild:
            # reads a DM message and sends to Descend if the author is in the Descend Server
            mutual_guilds = message.author.guilds
            if mutual_guilds:
                # check is author is in descend. Checking COMMAND_GUILD_SCOPE for that, since that already has the id and doesn't break testing
                allowed_guilds = [await client.get_guild(guild_id) for guild_id in COMMAND_GUILD_SCOPE]
                mutual_allowed_guilds = [g for g in allowed_guilds if g.id in mutual_guilds]

                if mutual_allowed_guilds:
                    thread_name = (
                        f"Message from {message.author.username}_{message.author.discriminator}|{message.author.id}"
                    )
                    channel: GuildText = await client.get_channel(descend_admin_channel_id) or await client.get_channel(
                        bot_dev_channel_id
                    )

                    # we just need to get the url, no need to re-upload
                    attached_files = [attachment.url for attachment in message.attachments]

                    # before we send a message, check the cache to see if we already made a thread for that user
                    if message.author.id in reply_cache.user_to_thread:
                        thread = reply_cache.user_to_thread[message.author.id]

                    else:
                        # todo correct function to get all threads for that channel if that exists
                        channel_threads = (
                            await channel.get_public_archived_threads()
                        ).threads + await channel.get_active_threads()

                        # maybe a thread does exist, but is not cached since we restarted
                        threads = [thread for thread in channel_threads if thread.name == thread_name]

                        if threads:
                            # only one entry
                            thread = threads[0]

                        else:
                            # create a thread
                            thread = await channel.create_thread_without_message(
                                name=thread_name,
                                thread_type=ChannelTypes.GUILD_PUBLIC_THREAD,
                                auto_archive_duration=AutoArchiveDuration.ONE_HOUR,
                                reason="Received DM",
                            )

                            # first message in thread
                            await thread.send(
                                embeds=embed_message(
                                    f"Inquiry from {message.author.display_name}",
                                    "Any message you send here is relayed to them, be careful what you type :)",
                                )
                            )

                        # save in cache
                        reply_cache.user_to_thread.update({message.author.id: thread})
                        reply_cache.thread_to_user.update({thread: message.author.id})

                    await thread.send(content=message.content)
                    for url in attached_files:
                        await thread.send(content=url)
