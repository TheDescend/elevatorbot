import datetime
from typing import Optional

from pydantic import BaseModel


class DestinyClanModel(BaseModel):
    id: int
    name: str


class DestinyClanMemberModel(BaseModel):
    system: int
    destiny_id: int
    name: str
    is_online: bool
    last_online_status_change: datetime.datetime
    join_date: datetime.datetime
    discord_id: Optional[int] = None


class DestinyClanMembersModel(BaseModel):
    members: list[DestinyClanMemberModel]


class DestinyClanLink(BaseModel):
    success: bool
    clan_name: str
