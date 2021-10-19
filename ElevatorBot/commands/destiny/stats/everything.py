from discord.ext.commands import Cog
from discord_slash import cog_ext
from discord_slash import SlashContext

from ElevatorBot.commandHelpers.optionTemplates import default_stat_option
from ElevatorBot.commandHelpers.optionTemplates import default_user_option


class StatEverything(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="stat",
        base_description="Shows you various Destiny 2 stats",
        name="everything",
        description="Displays information for all activities",
        options=[default_stat_option(), default_user_option()],
    )
    async def _stat_everything(self, ctx: SlashContext, **kwargs):
        pass


def setup(client):
    client.add_cog(StatEverything(client))
