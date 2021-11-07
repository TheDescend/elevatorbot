import datetime
from typing import Optional

from pydantic import BaseModel


class DestinyLowManModel(BaseModel):
    activity_ids: list[int]
    count: int
    flawless_count: int
    not_flawless_count: int

    fastest: datetime.timedelta = None


class DestinyActivityModel(BaseModel):
    name: str
    description: str
    activity_ids: list[int]


class DestinyActivitiesModel(BaseModel):
    activities = list[DestinyActivityModel]


class DestinyActivityDetailsUsersModel(BaseModel):
    bungie_name: str
    destiny_id: int
    system: int
    character_id: int
    character_class: str
    light_level: int
    completed: bool
    kills: int
    deaths: int
    assists: int
    time_played_seconds: int


class DestinyActivityDetailsModel(BaseModel):
    instance_id: int
    reference_id: int
    period: datetime.datetime
    starting_phase_index: int
    activity_duration_seconds: int
    score: int
    users: list[DestinyActivityDetailsUsersModel] = []


class DestinyLastInputModel(BaseModel):
    completed: bool
    activity_ids: Optional[list[int]] = None  # if this is supplied, mode is ignored
    mode: Optional[int] = None
    character_class: Optional[str] = None


class DestinyActivityInputModel(BaseModel):
    activity_ids: Optional[list[int]] = None
    mode: Optional[int] = (None,)
    character_class: Optional[str] = None
    character_ids: Optional[list[int]] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None


class DestinyActivityOutputModel(BaseModel):
    full_completions: int
    cp_completions: int
    kills: int
    precision_kills: int
    deaths: int
    assists: int
    time_spend: datetime.timedelta
    fastest: Optional[datetime.timedelta]  # only includes full runs
    fastest_instance_id: Optional[int]
    average: datetime.timedelta
