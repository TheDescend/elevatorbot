from discord.ext import commands
from discord_slash import cog_ext, SlashContext, ButtonStyle
from discord_slash.utils import manage_components
from discord_slash.utils.manage_commands import create_option

from functions.formating import embed_message
from functions.funWithButtons import TicTacToeGame, Calculator
from static.config import GUILD_IDS


class Games(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="tictactoe",
        description="Try to beat me in a tic tac toe game. First person to win again me in normal mode gets a free nitro",
        options=[
            create_option(
                name="easy_mode",
                description="Set this to true if you are too weak for the normal mode",
                option_type=5,
                required=False
            ),
        ],
    )
    async def _tictactoe(self, ctx: SlashContext, easy_mode: bool = False):
        game = TicTacToeGame(ctx=ctx, easy_mode=easy_mode)
        await game.play_game()

    @cog_ext.cog_slash(
        name="calculator",
        description="A handy calculator!",
        guild_ids=GUILD_IDS
    )
    async def _calculator(self, ctx: SlashContext):
        calc = Calculator(ctx)
        await calc.start()


def setup(client):
    client.add_cog(Games(client))
