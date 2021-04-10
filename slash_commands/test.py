import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from static.config import GUILD_IDS


class Test(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name="test", guild_ids=GUILD_IDS)
    async def _test(self, ctx: SlashContext):
        await ctx.defer()
        await ctx.send("Pong!")


# this is required
def setup(client):
    client.add_cog(Test(client))
