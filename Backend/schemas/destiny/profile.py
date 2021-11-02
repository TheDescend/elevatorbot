from pydantic import BaseModel

from Backend.schemas.destiny.activities import DestinyLowManModel


class DestinyProfileModel(BaseModel):
    discord_id: int
    destiny_id: int
    system: int

    class Config:
        orm_mode = True


class DestinyHasTokenModel(BaseModel):
    token: bool


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
