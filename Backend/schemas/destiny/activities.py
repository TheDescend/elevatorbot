import datetime

from pydantic import BaseModel


class DestinyLowManModel(BaseModel):
    activity_ids: list[int]
    count: int
    flawless_count: int
    not_flawless_count: int

    fastest: datetime.timedelta = None
