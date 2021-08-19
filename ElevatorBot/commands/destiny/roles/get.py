from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class RoleGet(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_subcommand(
        base="roles",
        base_description="Various commands concerning Destiny 2 achievement discord roles",
        name="get",
        description="Assigns you all the roles you've earned",
        options=[get_user_option(description="Requires elevated permissions")],
    )
    async def _roles_get(
        self,
        ctx: SlashContext,
        **kwargs
    ):
        pass


def setup(
    client
):
    client.add_cog(RoleGet(client))
