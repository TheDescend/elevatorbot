from pydantic import BaseModel


class DiscordProfileModel(BaseModel):
    discord_id: int
    destiny_id: int
    system: int

    class Config:
        orm_mode = True
