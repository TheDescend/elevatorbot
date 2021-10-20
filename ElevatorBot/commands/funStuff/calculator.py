from dis_snek.models import InteractionContext
from dis_snek.models import slash_command

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.funStuff.calculator import Calculator


class CalculatorCommand(BaseScale):
    @slash_command(name="calculator", description="A handy calculator!")
    async def _calculator(self, ctx: InteractionContext):

        calc = Calculator(ctx)
        await calc.start()


def setup(client):
    CalculatorCommand(client)
