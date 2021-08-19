from discord.ext import commands
from discord_slash import SlashContext, cog_ext


class ExampleCommand(commands.Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(
        name="example",
        description="Example Command",
    )
    async def _example(
        self,
        ctx: SlashContext
    ):
        await ctx.send("Example")


def setup(
    client
):
    client.add_cog(ExampleCommand(client))
