from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext


class TournamentStart(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_subcommand(
        base="tournament",
        base_description="Everything you need for in-house PvP tournaments",
        name="start",
        description="Starts the tournament. Can only be used by the user who used '/tournament _insert' or an Admin",
    )
    async def _start(
        self,
        ctx: SlashContext
    ):
        pass


def setup(
    client
):
    client.add_cog(TournamentStart(client))
