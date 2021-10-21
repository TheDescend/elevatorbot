import datetime
import logging
import traceback

from dis_snek.models import ComponentContext, InteractionContext

from ElevatorBot.misc.formating import embed_message

elevator_permission_bits = 536299961937


def get_now_with_tz() -> datetime.datetime:
    """Returns the current datetime (timezone aware)"""

    return datetime.datetime.now(tz=datetime.timezone.utc)


def localize_datetime(obj: datetime.datetime) -> datetime.datetime:
    """Returns a timezone aware object, localized to the system timezone"""

    return obj.astimezone()


async def log_error(
    ctx: InteractionContext | ComponentContext,
    error: Exception,
    situation: str,
) -> None:
    """Respond to the context and log error"""

    if not ctx.responded:
        await ctx.send(
            embeds=embed_message(
                "Error",
                f"Sorry, something went wrong\nThe Error has been logged and will be worked on",
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
