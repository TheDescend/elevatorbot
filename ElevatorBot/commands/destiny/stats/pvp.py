from discord.ext.commands import Cog
from discord_slash import cog_ext
from discord_slash import SlashContext

from ElevatorBot.commandHelpers.optionTemplates import default_stat_option
from ElevatorBot.commandHelpers.optionTemplates import default_user_option


class StatPvP(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="stat",
        base_description="Shows you various Destiny 2 stats",
        name="pvp",
        description="Displays information for all PvP activities",
        options=[default_stat_option(), default_user_option()],
    )
    async def _stat_pvp(self, ctx: SlashContext, **kwargs):
        pass


def setup(client):
    client.add_cog(StatPvP(client))
