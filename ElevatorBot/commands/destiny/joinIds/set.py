from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class IdSet(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="id",
        base_description="Steam IDs which can be used to join people in Destiny 2 without adding them as a friend",
        name="set",
        description="Set your Steam ID",
        options=[
            create_option(
                name="steamid",
                description="Your Steam ID which you want to set",
                option_type=3,
                required=True,
            ),
            get_user_option(description="Requires elevated permissions"),
        ],
    )
    async def _set(self, ctx: SlashContext, **kwargs):
        pass


def setup(client):
    client.add_cog(IdSet(client))
