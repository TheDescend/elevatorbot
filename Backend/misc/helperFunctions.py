from __future__ import annotations

import dataclasses
import datetime
from typing import Any, Generator, Optional

import dateutil.parser


def get_now_with_tz() -> datetime.datetime:
    """Returns the current datetime (timezone aware)"""

    return datetime.datetime.now(tz=datetime.timezone.utc)


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

    result = {}
    for name, value in kwargs.items():
        if value is not None:
            result.update({name: value})
    return result


def make_progress_bar_text(percentage: float) -> str:
    """Get the fancy progress bar used by seasonal challenges and catalysts"""

    bar_length = 10
    bar_text = ""
    for i in range(bar_length):
        if round(percentage, 1) <= 1 / bar_length * i:
            bar_text += "░"
        else:
            bar_text += "▓"

    return bar_text
