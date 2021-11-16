from typing import Optional

from dis_snek.models import Guild, GuildChannel, Role, ThreadChannel

from ElevatorBot.backendNetworking.misc.elevatorInfo import ElevatorGuilds


async def on_channel_delete(channel: GuildChannel):
    """Triggers when a channel gets deleted"""

    # todo
    pass


async def on_channel_create(channel: GuildChannel):
    """Triggers when a channel gets created"""

    # todo
    pass


# todo wrong parms in dis-snek currently
async def on_channel_update(before: GuildChannel, after: GuildChannel):
    """Triggers when a channel gets updated"""

    # todo
    pass


async def on_guild_join(guild: Guild):
    """Triggers when ElevatorBot gets added to a guild"""

    # todo make sure elevator has the correct permissions: elevator_permission_bits - otherwise break

    # todo make sure all current guilds are in the db too
    # add guild to the list of all guilds, needed for website info
    elevator_guilds = ElevatorGuilds(ctx=None, discord_guild=guild)
    await elevator_guilds.add()


async def on_guild_left(guild: Optional[Guild], guild_id: int):
    """Triggers when ElevatorBot gets removed from a guild"""

    # remove guild from the list of all guilds, needed for website info
    elevator_guilds = ElevatorGuilds(ctx=None, discord_guild=guild)
    await elevator_guilds.delete(guild_id=guild_id)


async def on_role_delete(role_id: int, guild_id: int):
    """Triggers when a role gets deleted"""

    # todo make sure to delete db entries for roles
    pass


async def on_role_update(before: Role, after: Role, guild_id: int):
    """Triggers when a role gets updated"""

    # todo
    pass


async def on_thread_create(thread: ThreadChannel):
    """Triggers when a thread gets created"""

    # todo
    pass


# todo wrong parms in dis-snek currently
async def on_thread_update(before: ThreadChannel, after: ThreadChannel):
    """Triggers when a thread gets updated"""

    # todo
    pass


async def on_thread_delete(thread: ThreadChannel):
    """Triggers when a thread gets deleted"""

    # todo
    pass
