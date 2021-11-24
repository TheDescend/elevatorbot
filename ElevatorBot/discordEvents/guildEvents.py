from typing import Optional

from dis_snek.models import Guild, GuildChannel, Role, ThreadChannel
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

from ElevatorBot.backendNetworking.misc.elevatorInfo import ElevatorGuilds


async def on_channel_delete(event: ChannelDelete):
    """Triggers when a channel gets deleted"""

    client = event.bot

    # todo remove persistent message / lfg message definition
    pass


async def on_channel_create(event: ChannelCreate):
    """Triggers when a channel gets created"""

    client = event.bot

    # todo
    pass


# todo wrong parms in dis-snek currently
async def on_channel_update(event: ChannelUpdate):
    """Triggers when a channel gets updated"""

    client = event.bot

    # todo
    pass


async def on_guild_join(event: GuildJoin):
    """Triggers when ElevatorBot gets added to a guild"""

    client = event.bot

    # todo make sure elevator has the correct permissions: elevator_permission_bits - otherwise break

    # todo make sure all current guilds are in the db too
    # add guild to the list of all guilds, needed for website info
    elevator_guilds = ElevatorGuilds(ctx=None, discord_guild=event.guild)
    await elevator_guilds.add()


async def on_guild_left(event: GuildLeft):
    """Triggers when ElevatorBot gets removed from a guild"""

    client = event.bot

    # remove guild from the list of all guilds, needed for website info
    elevator_guilds = ElevatorGuilds(ctx=None, discord_guild=event.guild)
    await elevator_guilds.delete(guild_id=event.guild_id)


async def on_role_delete(event: RoleDelete):
    """Triggers when a role gets deleted"""

    client = event.bot

    # todo make sure to delete db entries for roles
    pass


async def on_role_update(event: RoleUpdate):
    """Triggers when a role gets updated"""

    client = event.bot

    # todo
    pass


async def on_thread_create(event: ThreadCreate):
    """Triggers when a thread gets created"""

    client = event.bot

    # todo
    pass


# todo wrong parms in dis-snek currently
async def on_thread_update(event: ThreadUpdate):
    """Triggers when a thread gets updated"""

    client = event.bot

    # todo
    pass


async def on_thread_delete(event: ThreadDelete):
    """Triggers when a thread gets deleted"""

    client = event.bot

    # todo remove reply chach threads
    pass
