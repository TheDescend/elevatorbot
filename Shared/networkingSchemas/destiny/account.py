import datetime
from typing import Optional

from Shared.networkingSchemas.base import CustomBaseModel
from Shared.networkingSchemas.basic import BoolModel
from Shared.networkingSchemas.destiny.activities import DestinyLowManModel


class BoolModelObjective(CustomBaseModel):
    objective_id: int
    bool: bool


class BoolModelRecord(BoolModel):
    # this is empty if the triumph is earned
    objectives: list[BoolModelObjective] = []


class DestinyCharacterModel(CustomBaseModel):
    character_id: int
    character_class: str
    character_race: str
    character_gender: str


class DestinyCharactersModel(CustomBaseModel):
    characters: list[DestinyCharacterModel] = []


class DestinyTimeModel(CustomBaseModel):
    time_played: int  # in seconds
    mode: Optional[int] = None
    activity_ids: Optional[list[int]] = None


class DestinyTimesModel(CustomBaseModel):
    entries: list[DestinyTimeModel] = []


class DestinyStatInputModel(CustomBaseModel):
    stat_name: str
    stat_category: str


class DestinyTimeInputModel(CustomBaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    modes: list[int]
    activity_ids: Optional[list[int]] = None  # if this is supplied, mode is ignored
    character_class: Optional[str] = None


class DestinyUpdatedLowManModel(DestinyLowManModel):
    activity_name: str


class DestinyLowMansModel(CustomBaseModel):
    solos: list[DestinyUpdatedLowManModel] = []
    category: Optional[str] = None


class DestinyLowMansByCategoryModel(CustomBaseModel):
    categories: list[DestinyLowMansModel] = []


class SeasonalChallengesRecordModel(CustomBaseModel):
    record_id: int
    name: str
    description: str
    completion_percentage: Optional[float] = None
    completion_status: Optional[str] = None


class SeasonalChallengesTopicsModel(CustomBaseModel):
    name: str
    seasonal_challenges: list[SeasonalChallengesRecordModel] = []


class SeasonalChallengesModel(CustomBaseModel):
    topics: list[SeasonalChallengesTopicsModel] = []


class DestinyTriumphScoreModel(CustomBaseModel):
    active_score: int
    legacy_score: int
    lifetime_score: int


class DestinyCatalystModel(CustomBaseModel):
    name: str
    complete: bool
    completion_percentage: float
    completion_status: str


class DestinyCatalystsModel(CustomBaseModel):
    kinetic: list[DestinyCatalystModel] = []
    energy: list[DestinyCatalystModel] = []
    power: list[DestinyCatalystModel] = []

    completed: int = 0


class DestinyRecordModel(CustomBaseModel):
    name: str
    description: str
    completed: bool


class DestinySealModel(CustomBaseModel):
    name: str
    description: str
    completed: bool
    completion_percentage: float
    completion_status: str
    records: list[DestinyRecordModel] = []


class DestinySealsModel(CustomBaseModel):
    completed: list[DestinySealModel] = []
    not_completed: list[DestinySealModel] = []
    guilded: list[DestinySealModel] = []
    not_guilded: list[DestinySealModel] = []


class DestinyCraftableModel(CustomBaseModel):
    data: dict
    pass
