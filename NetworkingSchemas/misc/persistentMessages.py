from typing import Optional

from NetworkingSchemas.base import CustomBaseModel


class PersistentMessage(CustomBaseModel):
    message_name: str
    guild_id: int
    channel_id: int
    message_id: Optional[int] = None

    class Config:
        orm_mode = True


class PersistentMessages(CustomBaseModel):
    messages: list[PersistentMessage]


class PersistentMessageUpsert(CustomBaseModel):
    channel_id: int
    message_id: Optional[int] = None


class PersistentMessageDeleteInput(CustomBaseModel):
    message_name: Optional[str] = None
    channel_id: Optional[int] = None
    message_id: Optional[int] = None
