from naff import slash_command

from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.calculator import Calculator
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext


class CalculatorCommand(BaseModule):
    @slash_command(name="calculator", description="Summons a handy calculator")
    async def calculator(self, ctx: ElevatorInteractionContext):

        calc = Calculator(ctx)
        await calc.start()


def setup(client):
    CalculatorCommand(client)
