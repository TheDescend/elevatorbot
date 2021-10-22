from dis_snek.models import InteractionContext, sub_command

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.ticTacToe import TicTacToeGame


class TicTacToeHuman(BaseScale):
    @sub_command(
        base_name="tictactoe",
        base_description="You know and love it - TicTacToe",
        sub_name="versus",
        sub_description="Play against other humans",
    )
    async def _tictactoe_versus(self, ctx: InteractionContext):
        game = TicTacToeGame(ctx=ctx, versus=True)
        await game.play_game()


def setup(client):
    TicTacToeHuman(client)
