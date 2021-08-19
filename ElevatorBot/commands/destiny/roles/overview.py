from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot_old.static.slashCommandOptions import options_user


class RoleOverview(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_subcommand(
        base="roles",
        base_description="Various commands concerning Destiny 2 achievement discord roles",
        name="overview",
        description="Shows you what roles you can still achieve in this clan",
        options=[options_user()],
    )
    async def _roles_overview(
        self,
        ctx: SlashContext,
        **kwargs
    ):
        pass


def setup(
    client
):
    client.add_cog(RoleOverview(client))
