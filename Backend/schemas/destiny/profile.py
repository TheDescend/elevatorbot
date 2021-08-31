from pydantic import BaseModel


class DestinyProfileModel(BaseModel):
    discord_id: int
    destiny_id: int
    system: int

    class Config:
        orm_mode = True