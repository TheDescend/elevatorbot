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
from ElevatorBot.backendNetworking.misc.elevatorInfo import ElevatorGuilds
from ElevatorBot.backendNetworking.misc.polls import BackendPolls
from ElevatorBot.core.misc.persistentMessages import PersistentMessages
from ElevatorBot.misc.cache import reply_cache
from ElevatorBot.static.descendOnlyIds import descend_channels


async def on_channel_delete(event: ChannelDelete):
    """Triggers when a channel gets deleted"""

    # remove all lfg stuff if the channel matches
    persistent_messages = PersistentMessages(ctx=None, guild=event.channel.guild, message_name="lfg_channel")
    data = await persistent_messages.get()
    if data and data.channel_id == event.channel.id:
        # this is the lfg channel. Delete all the data
        lfg = DestinyLfgSystem(ctx=None, client=event.bot, discord_guild=None)
        result = await lfg.delete_all(guild_id=event.channel.guild.id)
        if not result:
            raise LookupError

    # delete all persistent messages in that channel
    persistent_messages = PersistentMessages(ctx=None, guild=None, message_name=None)
    result = await persistent_messages.delete(channel_id=event.channel.id)
    if not result:
        raise LookupError


async def on_channel_create(event: ChannelCreate):
    """Triggers when a channel gets created"""

    pass


async def on_channel_update(event: ChannelUpdate):
    """Triggers when a channel gets updated"""

    pass


async def on_guild_join(event: GuildJoin):
    """Triggers when ElevatorBot gets added to a guild"""

    # add guild to the list of all guilds, needed for website info
    elevator_guilds = ElevatorGuilds(ctx=None, discord_guild=event.guild)
    await elevator_guilds.add()


async def on_guild_left(event: GuildLeft):
    """Triggers when ElevatorBot gets removed from a guild"""

    # remove guild from the list of all guilds, needed for website info
    elevator_guilds = ElevatorGuilds(ctx=None, discord_guild=event.guild)
    result = await elevator_guilds.delete(guild_id=event.guild_id)
    if not result:
        raise LookupError

    # remove all persistent messages
    persistent_messages = PersistentMessages(ctx=None, guild=None, message_name=None)
    result = await persistent_messages.delete_all(guild_id=event.guild_id)
    if not result:
        raise LookupError

    # remove all roles
    roles = DestinyRoles(ctx=None, client=event.bot, discord_member=None, discord_guild=None)
    result = await roles.delete_all(guild_id=event.guild_id)
    if not result:
        raise LookupError

    # remove all polls
    polls = BackendPolls(ctx=None, discord_member=None, guild=None)
    result = await polls.delete_all(guild_id=event.guild_id)
    if not result:
        raise LookupError

    # remove all lfg stuff
    lfg = DestinyLfgSystem(ctx=None, client=event.bot, discord_guild=None)
    result = await lfg.delete_all(guild_id=event.guild_id)
    if not result:
        raise LookupError


async def on_role_delete(event: RoleDelete):
    """Triggers when a role gets deleted"""

    # remove the role
    roles = DestinyRoles(ctx=None, client=event.bot, discord_member=None, discord_guild=None)
    result = await roles.delete(guild_id=event.guild_id, role_id=event.role_id)
    if not result:
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
