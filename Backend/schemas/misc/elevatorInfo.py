import datetime

from pydantic import BaseModel


class ElevatorGuildModel(BaseModel):
    guild_id: int
    join_date: datetime.datetime

    class Config:
        orm_mode = True


class ElevatorGuildsModel(BaseModel):
    guilds: list[ElevatorGuildModel]
