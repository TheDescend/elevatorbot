from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class RoleRequirements(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_subcommand(
        base="roles",
        base_description="Various commands concerning Destiny 2 achievement discord roles",
        name="requirements",
        description="Shows you what you need to do to get the specified role",
        options=[
            create_option(
                name="role",
                description="The name of the role you want to look up",
                option_type=8,
                required=True,
            ),
            get_user_option(),
        ],
    )
    async def _roles_requirements(
        self,
        ctx: SlashContext,
        **kwargs
    ):
        pass


def setup(
    client
):
    client.add_cog(RoleRequirements(client))
