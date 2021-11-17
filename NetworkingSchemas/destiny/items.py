from pydantic import BaseModel


class DestinyLoreModel(BaseModel):
    reference_id: int
    name: str
    description: str
    sub_title: str
    redacted: bool

    class Config:
        orm_mode = True


class DestinyAllLoreModel(BaseModel):
    items = list[DestinyLoreModel]
