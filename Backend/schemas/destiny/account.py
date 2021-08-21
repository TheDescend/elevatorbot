from pydantic import BaseModel


class DestinyNameModel(BaseModel):
    name: str
