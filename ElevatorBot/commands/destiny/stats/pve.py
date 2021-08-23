from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.commandHelpers.optionTemplates import get_stat_option, get_user_option


class StatPvE(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="stat",
        base_description="Shows you various Destiny 2 stats",
        name="pve",
        description="Displays information for all PvE activities",
        options=[get_stat_option(), get_user_option()],
    )
    async def _stat_pve(self, ctx: SlashContext, **kwargs):
        pass


def setup(client):
    client.add_cog(StatPvE(client))
