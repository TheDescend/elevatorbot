import datetime
import logging
import traceback
import zoneinfo
from typing import Optional

from dateutil.parser import ParserError, parse
from dis_snek.models import ComponentContext, InteractionContext

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.responseTemplates import (
    respond_invalid_time_input,
    respond_time_input_in_past,
)
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.emojis import custom_emojis


def get_now_with_tz() -> datetime.datetime:
    """Returns the current datetime (timezone aware)"""

    return datetime.datetime.now(tz=datetime.timezone.utc)


def get_min_with_tz() -> datetime.datetime:
    """Returns the minimum datetime (timezone aware)"""

    return datetime.datetime(year=2000, month=1, day=1, tzinfo=datetime.timezone.utc)


def localize_datetime(obj: datetime.datetime) -> datetime.datetime:
    """Returns a timezone aware object, localized to the system timezone"""

    return obj.astimezone()


async def parse_string_datetime(
    ctx: InteractionContext, time: str, timezone: str = "UTC"
) -> Optional[datetime.datetime]:
    """Parse an input time and return it, or None if that fails"""

    # get start time
    try:
        start_time = parse(time, dayfirst=True)
    except ParserError:
        await respond_invalid_time_input(ctx=ctx)
        return

    if not start_time.tzinfo:
        # make that timezone aware
        tz = zoneinfo.ZoneInfo(timezone)
        start_time = start_time.replace(tzinfo=tz)

    # make sure that is in the future
    if start_time < get_now_with_tz():
        await respond_time_input_in_past(ctx=ctx)
        return

    return start_time


async def parse_datetime_options(
    ctx: InteractionContext,
    expansion: Optional[str] = None,
    season: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> tuple[Optional[datetime.datetime], Optional[datetime.datetime]]:
    """
    Parse datetime options and return:

    (start_time, end_time)
    or (None, None) - if something went wrong
    """

    # test if the args are wrong
    wrong_args = False
    if expansion:
        if season or start_time or end_time:
            wrong_args = True
    if season:
        if start_time or end_time:
            wrong_args = True

    if wrong_args:
        await ctx.send(
            ephemeral=True,
            embeds=embed_message(
                "Error",
                f"You can only input the following three combinations. Either: \n{custom_emojis.enter} `expansion` \n{custom_emojis.enter} `season` \n{custom_emojis.enter} `start_time` and/or `end_time`",
            ),
        )
        return None, None

    # default values
    formatted_start_time = get_min_with_tz()
    formatted_end_time = get_now_with_tz()

    if expansion:
        parts = expansion.split("|")
        formatted_start_time = datetime.datetime.fromtimestamp(int(parts[1]), tz=datetime.timezone.utc)
        formatted_end_time = datetime.datetime.fromtimestamp(int(parts[2]), tz=datetime.timezone.utc)

    if season:
        parts = season.split("|")
        formatted_start_time = datetime.datetime.fromtimestamp(int(parts[1]), tz=datetime.timezone.utc)
        formatted_end_time = datetime.datetime.fromtimestamp(int(parts[2]), tz=datetime.timezone.utc)

    if start_time:
        formatted_start_time = await parse_string_datetime(ctx=ctx, time=start_time)
        if not formatted_start_time:
            return None, None

    if end_time:
        formatted_end_time = await parse_string_datetime(ctx=ctx, time=end_time)
        if not formatted_end_time:
            return None, None

    return formatted_start_time, formatted_end_time


async def log_error(
    ctx: Optional[InteractionContext | ComponentContext], error: Exception, logger: logging.Logger
) -> None:
    """Respond to the context and log error"""

    if not ctx.responded:
        await ctx.send(
            embeds=embed_message(
                "Error",
                "Sorry, something went wrong\nThe Error has been logged and will be worked on",
                str(error),
            )
        )

    # log the error
    logger.exception(
        f"InteractionID '{ctx.interaction_id}' - Error '{error}' - Traceback: \n{''.join(traceback.format_tb(error.__traceback__))}"
    )

    # raising error again to making deving easier
    raise error


async def get_character_ids_from_class(profile: DestinyAccount, destiny_class: str) -> Optional[list[int]]:
    """Return the users character_ids that fit the given class or None"""

    result = await profile.get_character_info()

    if not result:
        return

    # loop through the characters and return the correct ids
    character_ids = []
    for character in result.characters:
        if character.character_class == destiny_class:
            character_ids.append(character.character_id)

    return character_ids if character_ids else None
