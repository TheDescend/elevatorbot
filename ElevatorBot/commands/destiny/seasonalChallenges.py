from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class SeasonalChallenges(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(
        name="challenges",
        description="Shows you the seasonal challenges and your completion status",
        options=[get_user_option()],
    )
    async def _challenges(
        self,
        ctx: SlashContext,
        **kwargs
    ):
        pass


def setup(
    client
):
    client.add_cog(SeasonalChallenges(client))
