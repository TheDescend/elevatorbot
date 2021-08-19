from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option


class PollAdd(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_subcommand(
        base="poll",
        base_description="Making polls easy",
        name="add",
        description="Add an option to a poll",
        options=[
            create_option(
                name="poll_id",
                description="The id of the poll",
                option_type=3,
                required=True,
            ),
            create_option(
                name="option",
                description="The name the option should have",
                option_type=3,
                required=True,
            ),
        ],
    )
    async def _poll_add(
        self,
        ctx: SlashContext,
        poll_id: str,
        option: str
    ):
        pass


def setup(
    client
):
    client.add_cog(PollAdd(client))
