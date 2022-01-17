import datetime
from typing import Optional

from Shared.networkingSchemas.base import CustomBaseModel


class LfgOutputModel(CustomBaseModel):
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


class AllLfgOutputModel(CustomBaseModel):
    events: list[LfgOutputModel] = []


class AllLfgDeleteOutputModel(CustomBaseModel):
    event_ids: list[int]


class UserAllLfgOutputModel(CustomBaseModel):
    joined: list[LfgOutputModel] = []
    backup: list[LfgOutputModel] = []


class LfgCreateInputModel(CustomBaseModel):
    activity: str
    description: str
    start_time: datetime.datetime
    max_joined_members: int
    joined_members: list[int]
    backup_members: list[int]


class LfgUpdateInputModel(CustomBaseModel):
    channel_id: Optional[int] = None
    message_id: Optional[int] = None
    voice_channel_id: Optional[int] = None

    activity: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime.datetime] = None
    max_joined_members: Optional[int] = None
    joined_members: Optional[list[int]] = None
    backup_members: Optional[list[int]] = None
