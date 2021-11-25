from dis_snek.models import InteractionContext, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.subCommandTemplates import tictactoe_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.ticTacToe import TicTacToeGame


class TicTacToeAI(BaseScale):
    @slash_command(
        **tictactoe_sub_command,
        sub_cmd_name="computer",
        sub_cmd_description="Try to beat me in a tic tac toe game",
    )
    @slash_option(
        name="easy_mode",
        description="Set this to true if you are too weak for the normal mode",
        opt_type=OptionTypes.BOOLEAN,
        required=False,
    )
    async def _tic_tac_toe_ai(self, ctx: InteractionContext, easy_mode: bool = False):
        game = TicTacToeGame(ctx=ctx, easy_mode=easy_mode)
        await game.play_game()


def setup(client):
    TicTacToeAI(client)
