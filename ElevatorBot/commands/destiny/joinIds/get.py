from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class IdGet(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_subcommand(
        base="id",
        base_description="Steam IDs which can be used to join people in Destiny 2 without adding them as a friend",
        name="get",
        description="Get a Steam ID",
        options=[get_user_option()],
    )
    async def _get(
        self,
        ctx: SlashContext,
        **kwargs
    ):
        pass


def setup(
    client
):
    client.add_cog(IdGet(client))
