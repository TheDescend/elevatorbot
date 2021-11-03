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
