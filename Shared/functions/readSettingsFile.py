from typing import Any, Optional

import toml

_SETTINGS: Optional[dict] = None


def get_setting(key: str) -> Any:
    """Returns the value of the setting. Taken from settings.toml"""

    global _SETTINGS
    if not _SETTINGS:
        # populate the dict
        with open("./settings.toml", "r") as file:
            _SETTINGS = toml.load(file)

    return _SETTINGS[key]
