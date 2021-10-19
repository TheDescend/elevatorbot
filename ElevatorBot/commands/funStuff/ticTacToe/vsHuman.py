# from discord.ext.commands import Cog
# from discord_slash import SlashContext, cog_ext
#
#
# class TicTacToeHuman(Cog):
#     def __init__(self, client):
#         self.client = client
#
#     @cog_ext.cog_subcommand(
#         base="tictactoe",
#         base_description="You know and love it - TicTacToe",
#         name="versus",
#         description="Play against other humans",
#     )
#     async def _tictactoe_versus(self, ctx: SlashContext):
#         pass
#
#
# def setup(client):
#     TicTacToeHuman(client)
