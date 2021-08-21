from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext


# todo make sure when sb registers to delete any entires with the same destiny id
class Register(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(
        name="register",
        description="Link your Destiny 2 account with ElevatorBot",
    )
    async def _register(
        self,
        ctx: SlashContext
    ):
        pass


def setup(
    client
):
    client.add_cog(Register(client))
