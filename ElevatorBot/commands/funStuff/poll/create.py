from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option


class PollCreate(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_subcommand(
        base="poll",
        base_description="Making polls easy",
        name="insert",
        description="Create a poll",
        options=[
            create_option(
                name="name",
                description="The name the poll should have",
                option_type=3,
                required=True,
            ),
            create_option(
                name="description",
                description="The description the poll should have",
                option_type=3,
                required=True,
            ),
        ],
    )
    async def _poll_create(
        self,
        ctx: SlashContext,
        name: str,
        description: str
    ):
        pass


def setup(
    client
):
    client.add_cog(PollCreate(client))
