from typing import Optional

from pydantic import BaseModel


class PollChoice(BaseModel):
    name: str
    discord_ids: list[int]


class PollInsertSchema(BaseModel):
    name: str
    description: str
    author_id: int
    guild_id: int
    channel_id: int
    message_id: int
    choices: list[PollChoice] = []


class PollSchema(PollInsertSchema):
    id: int

    class Config:
        orm_mode = True


class PollUserInputSchema(BaseModel):
    choice_name: str


class PollUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    author_id: Optional[int] = None
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    message_id: Optional[int] = None
    choices: Optional[list[PollChoice]] = None
