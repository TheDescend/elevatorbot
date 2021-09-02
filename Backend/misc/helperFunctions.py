import datetime
from collections import defaultdict

import pytz


def get_now_with_tz() -> datetime.datetime:
    """Returns the current datetime (timezone aware)"""

    return datetime.datetime.now(tz=datetime.timezone.utc)


def localize_datetime(obj: datetime.datetime) -> datetime.datetime:
    """Returns a timezone aware object, localized to the system timezone"""

    return obj.astimezone()


def get_datetime_from_bungie_entry(string: str) -> datetime.datetime:
    """Converts the bungie string to a utc datetime obj"""

    return add_utc_tz(datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ"))


def add_utc_tz(obj: datetime.datetime) -> datetime.datetime:
    """Returns a timezone aware object, localized to utc"""

    return pytz.utc.localize(obj)


def defaultdictify(d: dict):
    """Converts a dictionary to a defaultdict. Returns a defaultdict"""

    if isinstance(d, dict):
        return defaultdict(lambda: None, {k: defaultdictify(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [defaultdictify(e) for e in d]
    else:
        return d
