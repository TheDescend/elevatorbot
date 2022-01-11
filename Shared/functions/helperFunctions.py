from __future__ import annotations

import datetime


def get_now_with_tz() -> datetime.datetime:
    """Returns the current datetime (timezone aware)"""

    return datetime.datetime.now(tz=datetime.timezone.utc)


def get_min_with_tz() -> datetime.datetime:
    """Returns the minimum datetime (timezone aware)"""

    return datetime.datetime(year=2000, month=1, day=1, tzinfo=datetime.timezone.utc)


def localize_datetime(obj: datetime.datetime) -> datetime.datetime:
    """Returns a timezone aware object, localized to the system timezone"""

    return obj.astimezone()
