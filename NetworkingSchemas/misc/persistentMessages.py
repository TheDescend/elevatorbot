from typing import Optional

from pydantic import BaseModel


class PersistentMessage(BaseModel):
    message_name: str
    guild_id: int
    channel_id: int
    message_id: int

    class Config:
        orm_mode = True


class PersistentMessageUpsert(BaseModel):
    channel_id: int
    message_id: Optional[int] = None
