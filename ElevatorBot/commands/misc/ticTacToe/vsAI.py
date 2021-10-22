from dis_snek.models import InteractionContext, OptionTypes, slash_option, sub_command

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.ticTacToe import TicTacToeGame


class TicTacToeAI(BaseScale):
    @sub_command(
        base_name="tictactoe",
        base_description="You know and love it - TicTacToe",
        sub_name="computer",
        sub_description="Try to beat me in a tic tac toe game",
    )
    @slash_option(
        name="easy_mode",
        description="Set this to true if you are too weak for the normal mode",
        opt_type=OptionTypes.BOOLEAN,
        required=False,
    )
    async def _tictactoe_ai(self, ctx: InteractionContext, easy_mode: bool = False):
        game = TicTacToeGame(ctx=ctx, easy_mode=easy_mode)
        await game.play_game()


def setup(client):
    TicTacToeAI(client)
