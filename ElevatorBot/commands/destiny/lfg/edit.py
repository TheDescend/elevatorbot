from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option


class LfgEdit(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="edit",
        description="When you fucked up and need to edit an event",
        options=[
            create_option(
                name="lfg_id",
                description="The lfg message id",
                option_type=4,
                required=True,
            ),
            create_option(
                name="section",
                description="What section to edit",
                option_type=3,
                required=True,
                choices=[
                    create_choice(name="Activity", value="Activity"),
                    create_choice(name="Description", value="Description"),
                    create_choice(name="Start Time", value="Start Time"),
                    create_choice(name="Maximum Members", value="Maximum Members"),
                ],
            ),
        ],
    )
    async def _edit(
        self,
        ctx: SlashContext,
        lfg_id,
        section
    ):
        pass


def setup(
    client
):
    client.add_cog(LfgEdit(client))
