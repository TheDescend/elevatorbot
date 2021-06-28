from discord.ext import commands
from discord_slash import cog_ext, SlashContext, ButtonStyle
from discord_slash.utils import manage_components

from functions.formating import embed_message
from functions.ticTacToe import TicTacToeGame
from static.config import GUILD_IDS


class TicTacToe(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="tictactoe",
        description="Try to beat me in a tic tac toe game. First person to win again me gets a free nitro",
    )
    async def _tictactoe(self, ctx: SlashContext):
        game = TicTacToeGame(ctx)
        await game.play_game()




def setup(client):
    client.add_cog(TicTacToe(client))
