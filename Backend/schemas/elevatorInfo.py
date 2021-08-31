from pydantic import BaseModel


class ElevatorGuildModel(BaseModel):
    guild_ids: list[int]
