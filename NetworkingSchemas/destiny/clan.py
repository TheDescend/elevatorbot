import datetime
from typing import Optional

from pydantic import BaseModel

from NetworkingSchemas.base import CustomBaseModel


class DestinyClanModel(CustomBaseModel):
    id: int
    name: str


class DestinyClanMemberModel(CustomBaseModel):
    system: int
    destiny_id: int
    name: str
    is_online: bool
    last_online_status_change: datetime.datetime
    join_date: datetime.datetime
    discord_id: Optional[int] = None


class DestinyClanMembersModel(CustomBaseModel):
    members: list[DestinyClanMemberModel]


class DestinyClanLink(CustomBaseModel):
    success: bool
    clan_name: str
