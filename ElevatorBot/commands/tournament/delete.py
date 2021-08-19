from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext


class TournamentDelete(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_subcommand(
        base="tournament",
        base_description="Everything you need for in-house PvP tournaments",
        name="delete",
        description="Delete the tournament. Can only be used by the user who used '/tournament insert' or an Admin",
    )
    async def _delete(
        self,
        ctx: SlashContext
    ):
        pass


def setup(
    client
):
    client.add_cog(TournamentDelete(client))
