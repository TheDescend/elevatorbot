import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class DestinyWeaponModel(BaseModel):
    name: str
    description: str
    flavor_text: str
    weapon_type: str
    weapon_slot: str
    damage_type: str
    ammo_type: str
    reference_ids: list[int]


class DestinyWeaponsModel(BaseModel):
    weapons: list[DestinyWeaponModel]


class DestinyWeaponStatsInputModel(BaseModel):
    weapon_ids: list[int]
    character_class: Optional[str] = None
    character_ids: Optional[list[int]] = None
    mode: Optional[int] = None
    activity_hashes: Optional[list[int]] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None


class DestinyWeaponStatsModel(BaseModel):
    total_kills: int
    total_precision_kills: int
    total_activities: int
    best_kills: int
    best_kills_activity_name: str
    best_kills_activity_id: int
    best_kills_date: datetime.datetime


class DestinyTopWeaponModel(BaseModel):
    ranking: int
    stat_value: int
    weapon_ids: list[int]
    weapon_name: str
    weapon_type: str
    weapon_tier: str
    weapon_damage_type: str
    weapon_ammo_type: str


class DestinyTopWeaponsModel(BaseModel):
    kinetic: list[DestinyTopWeaponModel] = []
    energy: list[DestinyTopWeaponModel] = []
    power: list[DestinyTopWeaponModel] = []


class DestinyTopWeaponsStatInputModelEnum(str, Enum):
    KILLS = "kills"
    PRECISION_KILLS = "precision_kills"


class DestinyTopWeaponsInputModel(BaseModel):
    stat: DestinyTopWeaponsStatInputModelEnum
    how_many_per_slot: int
    include_weapon_with_ids: Optional[list[int]] = None
    weapon_type: Optional[int] = None
    damage_type: Optional[int] = None
    character_class: Optional[str] = None
    character_ids: Optional[list[int]] = None
    mode: Optional[int] = None
    activity_hashes: Optional[list[int]] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
