from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class DiscordJoinDate(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(
        name="discordjoindate",
        description="Check your join date of this discord server",
        options=[get_user_option()],
    )
    async def _discordjoindate(
        self,
        ctx: SlashContext,
        **kwargs
    ):
        pass


def setup(
    client
):
    client.add_cog(DiscordJoinDate(client))
