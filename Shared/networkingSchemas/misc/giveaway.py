from Shared.networkingSchemas import CustomBaseModel


class GiveawayModel(CustomBaseModel):
    message_id: int
    author_id: int
    guild_id: int
    discord_ids: list[int]

    class Config:
        orm_mode = True
