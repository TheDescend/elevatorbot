import logging
import traceback
from typing import Union

from discord_slash import ComponentContext, SlashContext

from ElevatorBot.misc.formating import embed_message


async def on_slash_command_error(
    ctx: SlashContext,
    error: Exception
) -> None:
    """Gets triggered on slash errors"""

    await log_error(
        ctx=ctx,
        error=error,
        situation="commands"
    )


async def on_component_callback_error(
    ctx: ComponentContext,
    error: Exception
) -> None:
    """Gets triggered on component errors"""

    await log_error(
        ctx=ctx,
        error=error,
        situation="interactions"
    )


async def log_error(
    ctx: Union[SlashContext, ComponentContext],
    error: Exception,
    situation: str,
) -> None:
    """ Respond to the context and log error """

    if not ctx.responded:
        await ctx.send(
            embed=embed_message(
                "Error",
                f"Sorry, something went wrong. The Error has been logged and will be worked on",
                str(error),
            )
        )

    # log the error
    logger = logging.getLogger(situation)
    logger.exception(
        f"InteractionID '{ctx.interaction_id}' - Error {error} - Traceback: \n{''.join(traceback.format_tb(error.__traceback__))}"
    )

    # raising error again to making deving easier
    raise error
