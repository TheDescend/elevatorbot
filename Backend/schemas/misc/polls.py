from typing import Optional

from pydantic import BaseModel


class PollSchema(BaseModel):
    id: int
    name: str
    description: str
    data: dict
    author_id: int
    guild_id: int
    channel_id: int
    message_id: int

    class Config:
        orm_mode = True


class PollInsertSchema(BaseModel):
    name: str
    description: str
    data: dict
    author_id: int
    guild_id: int
    channel_id: int
    message_id: int


class PollUserInputSchema(BaseModel):
    choice_name: str
    user_id: int


class PollUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data: Optional[dict] = None
    author_id: Optional[int] = None
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    message_id: Optional[int] = None
