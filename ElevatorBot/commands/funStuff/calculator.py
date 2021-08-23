from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.core.funStuff.calculator import Calculator


class CalculatorCommand(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="calculator",
        description="A handy calculator!",
    )
    async def _calculator(self, ctx: SlashContext):
        """A handy calculator!"""

        calc = Calculator(ctx)
        await calc.start()


def setup(client):
    client.add_cog(CalculatorCommand(client))
