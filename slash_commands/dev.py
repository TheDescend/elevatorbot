from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from static.config import GUILD_IDS


class DevCommands(commands.Cog):
    def __init__(self, client):
        self.client = client


def setup(client):
    client.add_cog(DevCommands(client))