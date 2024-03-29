from naff.api.events import (
    ChannelCreate,
    ChannelDelete,
    ChannelUpdate,
    GuildJoin,
    GuildLeft,
    RoleDelete,
    RoleUpdate,
    ThreadCreate,
    ThreadDelete,
    ThreadUpdate,
)

from ElevatorBot.core.misc.persistentMessages import PersistentMessages
from ElevatorBot.misc.cache import reply_cache
from ElevatorBot.networking.destiny.lfgSystem import DestinyLfgSystem
from ElevatorBot.networking.destiny.roles import DestinyRoles
from ElevatorBot.networking.errors import BackendException
from ElevatorBot.networking.misc.elevatorInfo import ElevatorGuilds
from ElevatorBot.networking.misc.polls import BackendPolls
from ElevatorBot.static.descendOnlyIds import descend_channels


async def on_channel_delete(event: ChannelDelete):
    """Triggers when a channel gets deleted"""

    # remove all lfg stuff if the channel matches
    persistent_messages = PersistentMessages(ctx=None, guild=event.channel.guild, message_name="lfg_channel")
    try:
        data = await persistent_messages.get()
        if data and data.channel_id == event.channel.id:
            # this is the lfg channel. Delete all the data
            lfg = DestinyLfgSystem(ctx=None, discord_guild=None)
            # noinspection PyTypeChecker
            await lfg.delete_all(client=event.bot, guild_id=event.channel.guild.id)
    except BackendException:
        pass

    # delete all persistent messages in that channel
    persistent_messages = PersistentMessages(ctx=None, guild=event.channel.guild, message_name=None)
    try:
        await persistent_messages.delete(channel_id=event.channel.id)
    except BackendException:
        pass


async def on_channel_create(event: ChannelCreate):
    """Triggers when a channel gets created"""

    pass


async def on_channel_update(event: ChannelUpdate):
    """Triggers when a channel gets updated"""

    pass


async def on_guild_join(event: GuildJoin):
    """Triggers when ElevatorBot gets added to a guild"""

    # this gets called on startup. We don't want that
    if event.bot.is_ready:
        # add guild to the list of all guilds, needed for website info
        elevator_guilds = ElevatorGuilds(ctx=None, discord_guild=event.guild)
        await elevator_guilds.add()


async def on_guild_left(event: GuildLeft):
    """Triggers when ElevatorBot gets removed from a guild"""

    # remove guild from the list of all guilds, needed for website info
    elevator_guilds = ElevatorGuilds(ctx=None, discord_guild=None)
    try:
        await elevator_guilds.delete(guild_id=event.guild_id)
    except BackendException:
        pass

    # remove all persistent messages
    persistent_messages = PersistentMessages(ctx=None, guild=None, message_name=None)
    try:
        await persistent_messages.delete_all(guild_id=event.guild_id)
    except BackendException:
        pass

    # remove all roles
    roles = DestinyRoles(ctx=None, discord_member=None, discord_guild=None)
    try:
        await roles.delete_all(guild_id=event.guild_id)
    except BackendException:
        pass

    # remove all polls
    polls = BackendPolls(ctx=None, discord_member=None, guild=None)
    try:
        await polls.delete_all(guild_id=event.guild_id)
    except BackendException:
        pass

    # remove all lfg stuff
    lfg = DestinyLfgSystem(ctx=None, discord_guild=None)
    try:
        # noinspection PyTypeChecker
        await lfg.delete_all(client=event.bot, guild_id=event.guild_id)
    except BackendException:
        pass


async def on_role_delete(event: RoleDelete):
    """Triggers when a role gets deleted"""

    # remove the role
    roles = DestinyRoles(ctx=None, discord_member=None, discord_guild=None)
    try:
        await roles.delete(guild_id=event.guild_id, role_id=event.role.id)
    except BackendException:
        pass


async def on_role_update(event: RoleUpdate):
    """Triggers when a role gets updated"""

    pass


async def on_thread_create(event: ThreadCreate):
    """Triggers when a thread gets created"""

    pass


async def on_thread_update(event: ThreadUpdate):
    """Triggers when a thread gets updated"""

    pass


async def on_thread_delete(event: ThreadDelete):
    """Triggers when a thread gets deleted"""

    if not isinstance(event.thread, str) and event.thread.guild == descend_channels.guild:
        # remove the reply thread cache data
        if event.thread.id in reply_cache.thread_to_user:
            user_id = reply_cache.thread_to_user[event.thread.id]
            reply_cache.thread_to_user.pop(event.thread.id)
            reply_cache.user_to_thread.pop(user_id)
