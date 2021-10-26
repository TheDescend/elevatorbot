import datetime
import logging
import traceback
from typing import Optional

from dis_snek.models import ComponentContext, InteractionContext

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
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


async def get_character_ids_from_class(
    profile: DestinyAccount, destiny_class: str, ctx: InteractionContext = None
) -> Optional[list[int]]:
    """Return the users character_ids that fit the given class or None"""

    result = await profile.get_character_info()

    if not result:
        if ctx:
            await result.send_error_message(ctx=ctx)
        return

    # loop through the characters and return the correct ids
    character_ids = []
    for character in result.result["characters"]:
        if character["character_class"] == destiny_class:
            character_ids.append(character["character_id"])

    return character_ids if character_ids else None
