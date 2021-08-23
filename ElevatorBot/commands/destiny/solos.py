from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class Solos(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="solos",
        description="Shows you an overview of your Destiny 2 solo activity completions",
        options=[get_user_option()],
    )
    async def _solos(self, ctx: SlashContext, **kwargs):
        pass


def setup(client):
    client.add_cog(Solos(client))
