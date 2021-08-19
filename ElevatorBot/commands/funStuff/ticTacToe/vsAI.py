from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option


class TicTacToeAI(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_subcommand(
        base="tictactoe",
        base_description="You know and love it - TicTacToe",
        name="computer",
        description="Try to beat me in a tic tac toe game",
        options=[
            create_option(
                name="easy_mode",
                description="Set this to true if you are too weak for the normal mode",
                option_type=5,
                required=False,
            ),
        ],
    )
    async def _tictactoe_ai(
        self,
        ctx: SlashContext,
        easy_mode: bool = False
    ):
        pass


def setup(
    client
):
    client.add_cog(TicTacToeAI(client))
