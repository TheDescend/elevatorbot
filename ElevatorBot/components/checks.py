from dis_snek import ComponentContext

from ElevatorBot.commandHelpers.responseTemplates import respond_pending


async def check_pending(ctx: ComponentContext) -> bool:
    """Returns False is the author is pending"""

    if ctx.author.pending:
        await respond_pending(ctx)
        return False
    return True
