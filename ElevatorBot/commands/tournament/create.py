# from discord.ext.commands import Cog
# from discord_slash import SlashContext, cog_ext
#
#
# class TournamentCreate(Cog):
#     def __init__(self, client):
#         self.client = client
#
#     @cog_ext.cog_subcommand(
#         base="tournament",
#         base_description="Everything you need for in-house PvP tournaments",
#         name="create",
#         description="Opens up registration. Can only be used if no other tournament is currently running",
#     )
#     async def _create(self, ctx: SlashContext):
#         pass
#
#
# def setup(client):
#     TournamentCreate(client)
