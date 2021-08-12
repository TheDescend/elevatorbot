from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.functions.funWithButtons import TicTacToeGame, Calculator


class Games(commands.Cog):


    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_subcommand(
        base="tictactoe",
        base_description="You know and love it - TicTacToe",
        name="computer",
        description="Try to beat me in a tic tac toe game. First person to win again me in hard mode gets a free nitro",
        options=[
            create_option(
                name="easy_mode",
                description="Set this to true if you are too weak for the normal mode",
                option_type=5,
                required=False
            ),
        ]
    )
    async def _tictactoe_ai(
        self,
        ctx: SlashContext,
        easy_mode: bool = False
    ):
        game = TicTacToeGame(ctx=ctx, easy_mode=easy_mode)
        await game.play_game()


    @cog_ext.cog_subcommand(
        base="tictactoe",
        base_description="You know and love it - TicTacToe",
        name="versus",
        description="Play against other humans",
    )
    async def _tictactoe_versus(
        self,
        ctx: SlashContext
    ):
        game = TicTacToeGame(ctx=ctx, versus=True)
        await game.play_game()


    @cog_ext.cog_slash(
        name="calculator",
        description="A handy calculator!",
    )
    async def _calculator(
        self,
        ctx: SlashContext
    ):
        calc = Calculator(ctx)
        await calc.start()


def setup(
    client
):
    client.add_cog(Games(client))
