import datetime

from Shared.NetworkingSchemas.base import CustomBaseModel


class ElevatorGuildModel(CustomBaseModel):
    guild_id: int
    join_date: datetime.datetime

    class Config:
        orm_mode = True


class ElevatorGuildsModel(CustomBaseModel):
    guilds: list[ElevatorGuildModel]
