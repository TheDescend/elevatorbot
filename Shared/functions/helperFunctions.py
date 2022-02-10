from __future__ import annotations

import datetime
import inspect


def get_now_with_tz() -> datetime.datetime:
    """Returns the current datetime (timezone aware)"""

    return datetime.datetime.now(tz=datetime.timezone.utc)


def get_min_with_tz() -> datetime.datetime:
    """Returns the minimum datetime (timezone aware)"""

    return datetime.datetime(year=2000, month=1, day=1, tzinfo=datetime.timezone.utc)


def localize_datetime(obj: datetime.datetime) -> datetime.datetime:
    """Returns a timezone aware object, localized to the system timezone"""

    return obj.astimezone()


def get_class_name(method) -> str:
    """Get the name of the (first children) class that implements this method"""

    for cls in inspect.getmro(method.__self__.__class__):
        if method.__name__ in cls.__dict__:
            return cls.__name__
