from typing import Optional

from pydantic import BaseModel

from NetworkingSchemas.base import CustomBaseModel


class DestinyProfileModel(CustomBaseModel):
    discord_id: int
    destiny_id: int
    system: int
    bungie_name: str

    class Config:
        orm_mode = True


class DestinyHasTokenModel(CustomBaseModel):
    token: bool
    value: Optional[str] = None
