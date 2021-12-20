import datetime
from typing import Optional

from pydantic import BaseModel


class LfgOutputModel(BaseModel):
    id: int
    guild_id: int
    channel_id: int
    author_id: int
    activity: str
    description: str
    start_time: datetime.datetime
    max_joined_members: int
    joined_members: list[int]
    backup_members: list[int]
    creation_time: datetime.datetime
    message_id: Optional[int] = None
    voice_channel_id: Optional[int] = None
    voice_category_channel_id: Optional[int] = None

    class Config:
        orm_mode = True


class AllLfgOutputModel(BaseModel):
    events: list[LfgOutputModel] = []


class AllLfgDeleteOutputModel(BaseModel):
    event_ids: list[int]


class UserAllLfgOutputModel(BaseModel):
    joined: list[LfgOutputModel] = []
    backup: list[LfgOutputModel] = []


class LfgCreateInputModel(BaseModel):
    activity: str
    description: str
    start_time: datetime.datetime
    max_joined_members: int
    joined_members: list[int]
    backup_members: list[int]


class LfgUpdateInputModel(BaseModel):
    channel_id: Optional[int] = None
    message_id: Optional[int] = None
    voice_channel_id: Optional[int] = None

    activity: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime.datetime] = None
    max_joined_members: Optional[int] = None
    joined_members: Optional[list[int]] = None
    backup_members: Optional[list[int]] = None
