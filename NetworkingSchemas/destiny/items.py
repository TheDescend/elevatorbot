from typing import Optional

from pydantic import BaseModel

from NetworkingSchemas.base import CustomBaseModel


class DestinyLoreModel(CustomBaseModel):
    reference_id: int
    name: str
    description: str
    sub_title: Optional[str] = None
    redacted: bool

    class Config:
        orm_mode = True


class DestinyAllLoreModel(CustomBaseModel):
    items: list[DestinyLoreModel]
