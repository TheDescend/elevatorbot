from typing import Optional

from pydantic import BaseModel


class PersistentMessage(BaseModel):
    message_name: str
    guild_id: int
    channel_id: int
    message_id: int

    class Config:
        orm_mode = True


class PersistentMessages(BaseModel):
    messages: list[PersistentMessage]


class PersistentMessageUpsert(BaseModel):
    channel_id: int
    message_id: Optional[int] = None


class PersistentMessageDeleteInput(BaseModel):
    message_name: Optional[str] = None
    channel_id: Optional[int] = None
    message_id: Optional[int] = None
