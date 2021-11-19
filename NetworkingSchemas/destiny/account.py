import datetime
from typing import Optional

from pydantic import BaseModel

from NetworkingSchemas.basic import BoolModel
from NetworkingSchemas.destiny.activities import DestinyLowManModel


class BoolModelObjective(BaseModel):
    objective_id: int
    bool: bool


class BoolModelRecord(BoolModel):
    # this is empty if the triumph is earned
    objectives: list[BoolModelObjective] = []


class DestinyCharacterModel(BaseModel):
    character_id: int
    character_class: str
    character_race: str
    character_gender: str


class DestinyCharactersModel(BaseModel):
    characters: list[DestinyCharacterModel] = []


class DestinyTimeModel(BaseModel):
    mode: int = None
    activity_ids: list[int] = None
    time_played: int  # in seconds


class DestinyTimesModel(BaseModel):
    entries: list[DestinyTimeModel] = []


class DestinyStatInputModel(BaseModel):
    stat_name: str
    stat_category: str


class DestinyTimeInputModel(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    modes: list[int]
    activity_ids: Optional[list[int]]  # if this is supplied, mode is ignored
    character_class: Optional[str] = None


class DestinyUpdatedLowManModel(DestinyLowManModel):
    activity_name: str


class DestinyLowMansModel(BaseModel):
    solos: list[DestinyUpdatedLowManModel] = []


class SeasonalChallengesRecordModel(BaseModel):
    record_id: int
    name: str
    description: str
    completion_percentage: float = None
    completion_status: str = None


class SeasonalChallengesTopicsModel(BaseModel):
    name: str
    seasonal_challenges: list[SeasonalChallengesRecordModel] = []


class SeasonalChallengesModel(BaseModel):
    topics: list[SeasonalChallengesTopicsModel] = []


class DestinyTriumphScoreModel(BaseModel):
    active_score: int
    legacy_score: int
    lifetime_score: int
