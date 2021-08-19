from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class LfgRemove(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="remove",
        description="Remove a user from an lfg event",
        options=[
            create_option(
                name="lfg_id",
                description="The lfg message id",
                option_type=4,
                required=True,
            ),
            get_user_option(description="The user you want to add", required=True),
        ],
    )
    async def _remove(
        self,
        ctx: SlashContext,
        lfg_id,
        user
    ):
        pass


def setup(
    client
):
    client.add_cog(LfgRemove(client))
