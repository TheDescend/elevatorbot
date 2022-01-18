import datetime
from typing import Optional

from Shared.networkingSchemas.base import CustomBaseModel


class DestinyLowManModel(CustomBaseModel):
    activity_ids: list[int]
    count: int
    flawless_count: int
    not_flawless_count: int

    fastest: Optional[datetime.timedelta] = None
    fastest_instance_id: Optional[int] = None


class DestinyActivityModel(CustomBaseModel):
    name: str
    description: str
    matchmade: bool
    max_players: int
    activity_ids: list[int]
    mode: Optional[int] = None
    image_url: Optional[str] = None


class DestinyActivitiesModel(CustomBaseModel):
    activities: list[DestinyActivityModel]


class DestinyActivityDetailsUsersModel(CustomBaseModel):
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


class DestinyActivityDetailsModel(CustomBaseModel):
    instance_id: int
    reference_id: int
    period: datetime.datetime
    starting_phase_index: int
    activity_duration_seconds: int
    score: int
    users: list[DestinyActivityDetailsUsersModel] = []


class DestinyLastInputModel(CustomBaseModel):
    completed: bool  # if this is False, the activity does not need to be completed (but can be)
    activity_ids: Optional[list[int]] = None  # if this is supplied, mode is ignored
    mode: Optional[int] = None
    character_class: Optional[str] = None


class DestinyActivityInputModel(CustomBaseModel):
    activity_ids: Optional[list[int]] = None
    mode: Optional[int] = None
    character_class: Optional[str] = None
    character_ids: Optional[list[int]] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None

    # this is used to get the afk forges
    need_zero_kills: bool = False


class DestinyActivityOutputModel(CustomBaseModel):
    full_completions: int
    cp_completions: int
    kills: int
    precision_kills: int
    deaths: int
    assists: int
    time_spend: datetime.timedelta
    fastest: Optional[datetime.timedelta] = None  # only includes full runs
    fastest_instance_id: Optional[int] = None
    average: datetime.timedelta
