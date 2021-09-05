import datetime
from typing import Optional

from pydantic import BaseModel


class LfgOutputModel(BaseModel):
    id: int
    guild_id: int
    channel_id: int
    message_id: int
    author_id: int
    activity: str
    description: str
    start_time: datetime.datetime
    max_joined_members: int
    joined_members: list[int]
    alternate_members: list[int]
    creation_time: datetime.datetime
    voice_channel_id: Optional[int]

    class Config:
        orm_mode = True


class AllLfgOutputModel(BaseModel):
    events: list[LfgOutputModel] = []


class LfgCreateInputModel(BaseModel):
    channel_id: int
    message_id: int

    activity: str
    description: str
    start_time: datetime.datetime
    max_joined_members: int
    joined_members: list[int]
    alternate_members: list[int]


class LfgUpdateInputModel(BaseModel):
    channel_id: Optional[int]
    message_id: Optional[int]
    voice_channel_id: Optional[int]

    activity: Optional[str]
    description: Optional[str]
    start_time: Optional[datetime.datetime]
    max_joined_members: Optional[int]
    joined_members: Optional[list[int]]
    alternate_members: Optional[list[int]]
