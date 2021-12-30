from dis_snek.models import InteractionContext, slash_command

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.calculator import Calculator


class CalculatorCommand(BaseScale):
    @slash_command(name="calculator", description="Summons a handy calculator")
    async def _calculator(self, ctx: InteractionContext):

        calc = Calculator(ctx)
        await calc.start()


def setup(client):
    CalculatorCommand(client)
