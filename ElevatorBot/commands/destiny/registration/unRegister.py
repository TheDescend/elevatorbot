from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class UnRegister(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(
        name="unregisterdesc",
        description="Unlink your Destiny 2 account from ElevatorBot",
        options=[get_user_option(description="Requires elevated permissions")],
    )
    async def _unregisterdesc(
        self,
        ctx: SlashContext,
        **kwargs
    ):
        pass


def setup(
    client
):
    client.add_cog(UnRegister(client))
