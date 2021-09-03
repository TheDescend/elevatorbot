from pydantic import BaseModel

from Backend.schemas.destiny.activities import DestinyLowManModel


class DestinyProfileModel(BaseModel):
    discord_id: int
    destiny_id: int
    system: int

    class Config:
        orm_mode = True


class DestinyUpdatedLowManModel(DestinyLowManModel):
    activity_name: str


class DestinyLowMansModel(BaseModel):
    solos: list[DestinyUpdatedLowManModel] = []
