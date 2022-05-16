from dateparser.search import search_dates
from naff import Embed, Timestamp, TimestampStyles

from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.static.emojis import custom_emojis


async def get_timestamp_embed(search_string: str, parse_relative: bool = True) -> Embed | None:
    """Create an embed having all timestamps in the message"""

    dates = []

    # parse actual dates or times
    if absolute_dates := search_dates(
        search_string,
        languages=["en"],
        settings={"PREFER_DATES_FROM": "future", "DATE_ORDER": "DMY", "PARSERS": ["absolute-time"]},
    ):
        # only use datetimes that have a timezone attached
        dates = [date for date in absolute_dates if date[1].tzinfo]

    # parse relative times
    if parse_relative:
        if relative_dates := search_dates(
            search_string,
            languages=["en"],
            settings={
                "PREFER_DATES_FROM": "future",
                "RETURN_TIME_AS_PERIOD": True,
                "PARSERS": ["relative-time"],
            },
        ):
            dates.extend(relative_dates)

    # format the dates
    if dates:
        # add the texts
        text = []
        for date in dates:
            timestamp = Timestamp.fromdatetime(date[1])
            time_text = f"{timestamp.format(style=TimestampStyles.ShortDateTime)} - {timestamp.format(style=TimestampStyles.RelativeTime)}"
            text.append(f"`{date[0]}`\n{custom_emojis.enter} {time_text}")

        return embed_message(description="\n".join(text))
