from ElevatorBot.commandHelpers.responseTemplates import respond_pending
from ElevatorBot.discordEvents.customInteractions import ElevatorComponentContext


async def check_pending(ctx: ElevatorComponentContext) -> bool:
    """Returns False is the author is pending"""

    if ctx.author.pending:
        await respond_pending(ctx)
        return False
    return True
