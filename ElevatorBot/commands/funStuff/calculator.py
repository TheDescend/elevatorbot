from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext


class Calculator(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(
        name="calculator",
        description="A handy calculator!",
    )
    async def _calculator(
        self,
        ctx: SlashContext
    ):
        pass


def setup(
    client
):
    client.add_cog(Calculator(client))
