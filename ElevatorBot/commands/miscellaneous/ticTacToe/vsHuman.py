from dis_snek.models import InteractionContext, slash_command

from ElevatorBot.commandHelpers.subCommandTemplates import tictactoe_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.ticTacToe import TicTacToeGame


class TicTacToeHuman(BaseScale):
    @slash_command(
        **tictactoe_sub_command,
        sub_cmd_name="versus",
        sub_cmd_description="Play against other humans",
    )
    async def versus(self, ctx: InteractionContext):
        game = TicTacToeGame(ctx=ctx, versus=True)
        await game.play_game()


def setup(client):
    TicTacToeHuman(client)
