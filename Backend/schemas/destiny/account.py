from pydantic import BaseModel


class DestinyNameModel(BaseModel):
    name: str


class DestinyStatModel(BaseModel):
    value: int | float


class DestinyCharacterModel(BaseModel):
    character_id: int
    character_class: str
    character_race: str
    character_gender: str


class DestinyCharactersModel(BaseModel):
    characters: list[DestinyCharacterModel] = []
