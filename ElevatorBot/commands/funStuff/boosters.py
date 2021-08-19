from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext


class Boosters(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(name="boosters", description="Prints all premium subscribers")
    async def _boosters(
        self,
        ctx: SlashContext
    ):
        pass


def setup(
    client
):
    client.add_cog(Boosters(client))
