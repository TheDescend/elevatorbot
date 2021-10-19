from dis_snek.models import ComponentContext
from dis_snek.models import InteractionContext

from ElevatorBot.misc.helperFunctions import log_error


async def on_command_error(ctx: InteractionContext, error: Exception) -> None:
    """Gets triggered on slash errors"""

    await log_error(ctx=ctx, error=error, situation="commands")


async def on_component_callback_error(ctx: ComponentContext, error: Exception) -> None:
    """Gets triggered on component errors"""

    await log_error(ctx=ctx, error=error, situation="interactions")
