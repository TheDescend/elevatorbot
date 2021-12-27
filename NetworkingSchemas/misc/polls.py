from typing import Optional

from pydantic import BaseModel

from NetworkingSchemas.base import CustomBaseModel


class PollChoice(CustomBaseModel):
    name: str
    discord_ids: list[int]


class PollInsertSchema(CustomBaseModel):
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


class PollUserInputSchema(CustomBaseModel):
    choice_name: str


class PollUpdateSchema(CustomBaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    author_id: Optional[int] = None
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    message_id: Optional[int] = None
    choices: Optional[list[PollChoice]] = None
