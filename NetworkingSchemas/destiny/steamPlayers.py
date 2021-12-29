import datetime

from NetworkingSchemas.base import CustomBaseModel


class DestinySteamPlayerCountModel(CustomBaseModel):
    date: datetime.date
    number_of_players: int

    class Config:
        orm_mode = True


class DestinySteamPlayersCountModel(CustomBaseModel):
    entries: list[DestinySteamPlayerCountModel] = []
