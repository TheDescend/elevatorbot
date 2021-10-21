from dis_snek.models import Guild, GuildChannel, Role, ThreadChannel

from ElevatorBot.backendNetworking.misc.elevatorInfo import ElevatorGuilds
from ElevatorBot.misc.helperFunctions import elevator_permission_bits


async def on_channel_delete(channel: GuildChannel):
    """ """
    # todo
    pass


async def on_channel_create(channel: GuildChannel):
    """ """
    # todo
    pass


async def on_channel_update(before: GuildChannel, after: GuildChannel):
    """ """
    # todo
    pass


async def on_guild_join(guild: Guild):
    """Triggers when ElevatorBot gets added to a guild"""

    # todo make sure elevator has the correct permissions: elevator_permission_bits - otherwise break

    # todo make sure all current guilds are in the db too
    # add guild to the list of all guilds, needed for website info
    elevator_guilds = ElevatorGuilds(discord_guild=guild)
    await elevator_guilds.add()


async def on_guild_remove(guild: Guild):
    """Triggers when ElevatorBot gets removed from a guild"""

    # remove guild from the list of all guilds, needed for website info
    elevator_guilds = ElevatorGuilds(discord_guild=guild)
    await elevator_guilds.delete()


async def on_guild_role_delete(role: Role):
    """ """
    # todo make sure to delete db entries for roles
    pass


async def on_guild_role_update(before: Role, after: Role):
    """ """
    # todo
    pass


async def on_thread_create(thread: ThreadChannel):
    """ """
    # todo
    pass


async def on_thread_update(before: ThreadChannel, after: ThreadChannel):
    """ """
    # todo
    pass


async def on_thread_delete(thread: ThreadChannel):
    """ """
    # todo
    pass
