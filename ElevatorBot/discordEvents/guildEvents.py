from dis_snek.models.events import (
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

from ElevatorBot.backendNetworking.destiny.lfgSystem import DestinyLfgSystem
from ElevatorBot.backendNetworking.destiny.roles import DestinyRoles
from ElevatorBot.backendNetworking.errors import BackendException
from ElevatorBot.backendNetworking.misc.elevatorInfo import ElevatorGuilds
from ElevatorBot.backendNetworking.misc.polls import BackendPolls
from ElevatorBot.core.misc.persistentMessages import PersistentMessages
from ElevatorBot.misc.cache import reply_cache
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
            await lfg.delete_all(client=event.bot, guild_id=event.channel.guild.id)
    except BackendException:
        pass

    # delete all persistent messages in that channel
    persistent_messages = PersistentMessages(ctx=None, guild=None, message_name=None)
    await persistent_messages.delete(channel_id=event.channel.id)


async def on_channel_create(event: ChannelCreate):
    """Triggers when a channel gets created"""

    pass


async def on_channel_update(event: ChannelUpdate):
    """Triggers when a channel gets updated"""

    pass


async def on_guild_join(event: GuildJoin):
    """Triggers when ElevatorBot gets added to a guild"""

    # todo wtf is this
    elevator_guilds = ElevatorGuilds(ctx=None, discord_guild=event.guild)
    activated_guild = event.guild
    guilds_saved = await elevator_guilds.get()
    if guilds_saved.success:
        guild_list = guilds_saved.result["guilds"]
    # {'guild_id': 223433090817720320, 'join_date': '2021-12-20T22:32:19.965987+00:00'}
    guild_id_list = [guild["guild_id"] for guild in guild_list]
    guild_id = activated_guild.id
    # this gets called on startup. We don't want that
    if not guild_id in guild_id_list:
        # add guild to the list of all guilds, needed for website info
        await elevator_guilds.add()


async def on_guild_left(event: GuildLeft):
    """Triggers when ElevatorBot gets removed from a guild"""

    # remove guild from the list of all guilds, needed for website info
    elevator_guilds = ElevatorGuilds(ctx=None, discord_guild=event.guild)
    try:
        await elevator_guilds.delete(guild_id=event.guild_id)
    except BackendException:
        raise LookupError

    # remove all persistent messages
    persistent_messages = PersistentMessages(ctx=None, guild=None, message_name=None)
    try:
        await persistent_messages.delete_all(guild_id=event.guild_id)
    except BackendException:
        raise LookupError

    # remove all roles
    roles = DestinyRoles(ctx=None, discord_member=None, discord_guild=None)
    try:
        await roles.delete_all(guild_id=event.guild_id)
    except BackendException:
        raise LookupError

    # remove all polls
    polls = BackendPolls(ctx=None, discord_member=None, guild=None)
    try:
        await polls.delete_all(guild_id=event.guild_id)
    except BackendException:
        raise LookupError

    # remove all lfg stuff
    lfg = DestinyLfgSystem(ctx=None, discord_guild=None)
    try:
        await lfg.delete_all(client=event.bot, guild_id=event.guild_id)
    except BackendException:
        raise LookupError


async def on_role_delete(event: RoleDelete):
    """Triggers when a role gets deleted"""

    # remove the role
    roles = DestinyRoles(ctx=None, discord_member=None, discord_guild=None)
    try:
        await roles.delete(guild_id=event.guild_id, role_id=event.role_id)
    except BackendException:
        raise LookupError


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

    if event.thread.guild == descend_channels.guild:
        # remove the reply thread cache data
        if event.thread in reply_cache.thread_to_user:
            user_id = reply_cache.thread_to_user[event.thread]
            reply_cache.thread_to_user.pop(event.thread)
            reply_cache.user_to_thread.pop(user_id)
