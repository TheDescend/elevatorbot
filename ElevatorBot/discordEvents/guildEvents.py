import discord.abc

from ElevatorBot.backendNetworking.misc.elevatorInfo import ElevatorGuilds


async def on_guild_channel_delete(channel: discord.abc.GuildChannel):
    """ """
    # todo
    pass


async def on_guild_channel_create(channel: discord.abc.GuildChannel):
    """ """
    # todo
    pass


async def on_guild_channel_update(before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
    """ """
    # todo
    pass


async def on_guild_join(guild: discord.Guild):
    """Triggers when ElevatorBot gets added to a guild"""

    # todo make sure all current guilds are in the db too
    # add guild to the list of all guilds, needed for website info
    elevator_guilds = ElevatorGuilds(discord_guild=guild)
    await elevator_guilds.add()


async def on_guild_remove(guild: discord.Guild):
    """Triggers when ElevatorBot gets removed from a guild"""

    # remove guild from the list of all guilds, needed for website info
    elevator_guilds = ElevatorGuilds(discord_guild=guild)
    await elevator_guilds.delete()


async def on_guild_role_delete(role: discord.Role):
    """ """
    # todo make sure to delete db entries for roles
    pass


async def on_guild_role_update(before: discord.Role, after: discord.Role):
    """ """
    # todo
    pass
