from typing import Optional

from pydantic import BaseModel


class DestinyProfileModel(BaseModel):
    discord_id: int
    destiny_id: int
    system: int
    bungie_name: str

    class Config:
        orm_mode = True


class DestinyHasTokenModel(BaseModel):
    token: bool
    value: Optional[str] = None
