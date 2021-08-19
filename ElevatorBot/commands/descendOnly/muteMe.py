from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class MuteMe(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(
        name="muteme",
        description="I wonder what this does...",
        options=[get_user_option()],
    )
    async def _muteme(
        self,
        ctx: SlashContext,
        **kwargs
    ):
        pass


def setup(
    client
):
    client.add_cog(MuteMe(client))
