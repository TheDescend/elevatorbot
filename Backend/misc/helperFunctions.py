from __future__ import annotations

import dataclasses
import datetime
from typing import Any, Generator, Optional

import dateutil.parser


def get_now_with_tz() -> datetime.datetime:
    """Returns the current datetime (timezone aware)"""

    return datetime.datetime.now(tz=datetime.timezone.utc)


def get_min_with_tz() -> datetime.datetime:
    """Returns the minimum datetime (timezone aware)"""

    return datetime.datetime(year=2000, month=1, day=1, tzinfo=datetime.timezone.utc)


def localize_datetime(obj: datetime.datetime) -> datetime.datetime:
    """Returns a timezone aware object, localized to the system timezone"""

    return obj.astimezone()


def get_datetime_from_bungie_entry(string: str) -> datetime.datetime:
    """Converts the bungie string to a utc datetime obj"""

    return dateutil.parser.parse(string)


@dataclasses.dataclass
class DefaultDict:
    """A dictionary that supports nested .get() calls which return None if the key does not exist"""

    _dict: dict

    def get(self, *keys: Any) -> Optional[Any]:
        """Get the key value or None"""

        depth = self._dict
        for key in keys:
            if key not in depth:
                return None
            depth = depth[key]
        return depth

    def items(self) -> Generator[tuple[str, DefaultDict]]:
        """Iterate over the items"""

        for key, value in self._dict.items():
            yield key, DefaultDict(value)


def convert_kwargs_into_dict(**kwargs) -> dict:
    """Convert kwargs that are not None into a dict"""

    return {key: value for key, value in kwargs.items() if value is not None}


def make_progress_bar_text(percentage: float, bar_length: int = 2) -> str:
    """
    Get the progress bar used by seasonal challenges and catalysts and more

    Translations:
        "A" -> Empty Emoji
        "B" -> Empty Emoji with edge
        "C" -> 1 Quarter Full Emoji
        "D" -> 2 Quarter Full Emoji
        "E" -> 3 Quarter Full Emoji
        "F" -> 4 Quarter Full Emoji
    """

    to_beat = 1 / bar_length / 4

    bar_text = ""
    for i in range(bar_length):
        # 100%
        if percentage >= (x := (to_beat * 4)):
            bar_text += "F"
            percentage -= x
        # 75%
        elif percentage >= (x := (to_beat * 3)):
            bar_text += "E"
            percentage -= x
        # 50%
        elif percentage >= (x := (to_beat * 2)):
            bar_text += "D"
            percentage -= x
        # 25%
        elif percentage >= (x := (to_beat * 1)):
            bar_text += "C"
            percentage -= x
        # 0%
        else:
            # if it's the first one or the last one was empty too, set it to completely empty
            if bar_text == "" or bar_text[-1:] != "F":
                bar_text += "A"
            # else keep the tiny edge
            else:
                bar_text += "B"

    return bar_text
