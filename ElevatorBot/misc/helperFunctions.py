import datetime
import logging
import os
import zoneinfo
from enum import Enum, EnumMeta
from typing import Generator, Optional

from dateutil.parser import ParserError, parse
from naff import Context, CustomEmoji
from naff.client.errors import HTTPException
from naff.models.naff.checks import TYPE_CHECK_FUNCTION

from ElevatorBot.commandHelpers.responseTemplates import respond_invalid_time_input, respond_time_input_in_past
from ElevatorBot.discordEvents.customInteractions import ElevatorComponentContext, ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.account import DestinyAccount
from ElevatorBot.static.emojis import custom_emojis
from Shared.enums.elevator import UnknownEnum
from Shared.functions.helperFunctions import get_min_with_tz, get_now_with_tz
from Shared.functions.readSettingsFile import get_setting


async def parse_string_datetime(
    ctx: ElevatorInteractionContext, time: str, timezone: str = "UTC", can_start_in_past: bool = True
) -> Optional[datetime.datetime]:
    """Parse an input time and return it, or None if that fails"""

    # get start time
    try:
        time = parse(time, dayfirst=True)
    except ParserError:
        await respond_invalid_time_input(ctx=ctx)
        return

    if not time.tzinfo:
        # make that timezone aware
        tz = zoneinfo.ZoneInfo(timezone)
        time = time.replace(tzinfo=tz)

    # make sure that is in the future
    if not can_start_in_past:
        if time < get_now_with_tz():
            await respond_time_input_in_past(ctx=ctx)
            return

    return time


async def parse_datetime_options(
    ctx: ElevatorInteractionContext,
    expansion: Optional[str] = None,
    season: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    can_start_in_past: bool = True,
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
        formatted_start_time = await parse_string_datetime(
            ctx=ctx, time=start_time, can_start_in_past=can_start_in_past
        )
        if not formatted_start_time:
            return None, None

    if end_time:
        formatted_end_time = await parse_string_datetime(ctx=ctx, time=end_time, can_start_in_past=can_start_in_past)
        if not formatted_end_time:
            return None, None

    return formatted_start_time, formatted_end_time


def parse_naff_errors(error: Exception) -> Optional[str]:
    """Parses naff error messages and logs that"""

    if isinstance(error, HTTPException):
        if error.errors:
            # HTTPException's are of 3 known formats, we can parse them for human-readable errors
            try:
                errors = error.search_for_message(error.errors)
                formatted = f"HTTPException: {error.status}|{error.response.reason}: " + "\n".join(errors)
            except TypeError:
                formatted = f"HTTPException: {error.status}|{error.response.reason}: {str(error.errors)}"

            return formatted


async def log_error(
    ctx: Optional[ElevatorInteractionContext | ElevatorComponentContext], error: Exception, logger: logging.Logger
) -> None:
    """Respond to the context and log error"""

    # get the command name or the component name
    if isinstance(ctx, ElevatorComponentContext):
        extra = f"CustomID `{ctx.custom_id}`"
    else:
        extra = f"CommandName `/{ctx.invoked_name}`"

    naff_errors = parse_naff_errors(error=error)

    # log the error
    msg = f"InteractionID `{ctx.interaction_id}` - {extra}"
    if naff_errors:
        msg += f" - NAFF Errors:\n{naff_errors}"
    logger.exception(msg, exc_info=error)

    if ctx and not ctx.responded:
        await ctx.send(
            embeds=embed_message(
                "Error",
                "Sorry, something went wrong\nThe Error has been logged and will be worked on",
            )
        )


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


def yield_files_in_folder(folder: str, extension: str) -> Generator:
    """Yields all paths of all files with the correct extension in the specified folder"""

    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(f".{extension}") and not file.startswith("__init__") and not file.startswith("base"):
                file = file.removesuffix(f".{extension}")
                path = os.path.join(root, file)
                yield path.replace("/", ".").replace("\\", ".")


def get_enum_by_name(enum_class: EnumMeta, key: str) -> Enum:
    """Gets the name of the enum"""

    # does it exist with the underscore?
    if res := getattr(enum_class, "_".join(key.split(" ")).upper(), None):
        return res

    # try without the underscore (MACHINEGUN), else return a question mark
    if res := getattr(enum_class, "_".join(key.split(" ")).upper().replace("_", ""), None):
        return res

    logging.getLogger("generalExceptions").warning(f"get_enum_by_name(): Could not find {key=} in {enum_class=}")
    return UnknownEnum.UNKNOWN


def get_emoji_by_name(enum_class: EnumMeta, key: str) -> CustomEmoji:
    """Gets the emoji of the enum"""

    enum = get_enum_by_name(enum_class=enum_class, key=key)

    return getattr(custom_emojis, enum.name.lower(), custom_emojis.question)


def check_is_guild() -> TYPE_CHECK_FUNCTION:
    """Check that the guild is correct"""

    async def check(ctx: Context) -> bool:
        return ctx.guild and ctx.guild.id in get_setting("COMMAND_GUILD_SCOPE")

    return check
