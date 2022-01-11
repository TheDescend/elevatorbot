import datetime
from typing import Optional

from Shared.NetworkingSchemas.base import CustomBaseModel


class ModerationModel(CustomBaseModel):
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


class ModerationsModel(CustomBaseModel):
    entries: list[ModerationModel] = []


class ModerationAddModel(CustomBaseModel):
    mod_discord_id: int
    reason: str
    duration_in_seconds: Optional[int] = None
