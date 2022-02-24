from __future__ import annotations

import dataclasses
import datetime
from typing import Any, Generator, Optional

import dateutil.parser


def get_datetime_from_bungie_entry(string: str) -> datetime.datetime:
    """Converts the bungie string to a utc datetime obj"""

    return dateutil.parser.parse(string)


@dataclasses.dataclass
class DefaultDict:
    """A dictionary that supports nested .get() calls which return None if the key does not exist"""

    _dict: dict

    def get(self, *keys: Any, default: Optional[Any] = None) -> Any:
        """Get the key value or None"""

        depth = self._dict
        for key in keys:
            if key not in depth:
                return default
            depth = depth[key]
        return depth

    def items(self) -> Generator[tuple[str, DefaultDict]]:
        """Iterate over the items"""

        for key, value in self._dict.items():
            yield key, DefaultDict(value)


def convert_kwargs_into_dict(**kwargs) -> dict:
    """Convert kwargs that are not None into a dict"""

    return {key: value for key, value in kwargs.items() if value is not None}
