from discord_slash import ComponentContext
from discord_slash import SlashContext

from ElevatorBot.misc.helperFunctions import log_error


async def on_component_callback_error(ctx: ComponentContext, error: Exception) -> None:
    """Gets triggered on component errors"""

    await log_error(ctx=ctx, error=error, situation="interactions")
