from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext


class FunFact(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(
        name="funfact", description="Very fun fun facts just for the funny fun of it"
    )
    async def _funfact(
        self,
        ctx: SlashContext
    ):
        pass


def setup(
    client
):
    client.add_cog(FunFact(client))
