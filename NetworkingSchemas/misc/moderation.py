import datetime
from typing import Optional

from pydantic import BaseModel


class ModerationModel(BaseModel):
    id: str
    guild_id: int
    discord_id: int
    mod_discord_id: int
    type: str
    reason: str
    date: datetime.datetime
    duration_in_seconds: Optional[int] = None

    class Config:
        orm_mode = True


class ModerationsModel(BaseModel):
    entries: list[ModerationModel] = []


class ModerationAddModel(BaseModel):
    mod_discord_id: int
    reason: str
    duration_in_seconds: Optional[int] = None
