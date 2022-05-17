from naff import slash_command

from ElevatorBot.commandHelpers.subCommandTemplates import tictactoe_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.ticTacToe import TicTacToeGame
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext


class TicTacToeHuman(BaseModule):
    @slash_command(
        **tictactoe_sub_command,
        sub_cmd_name="versus",
        sub_cmd_description="Play against other humans",
        dm_permission=False,
    )
    async def versus(self, ctx: ElevatorInteractionContext):
        game = TicTacToeGame(ctx=ctx, versus=True)
        await game.play_game()


def setup(client):
    TicTacToeHuman(client)
