import dataclasses
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.destiny.items import destiny_items
from Backend.database.enums import (
    DestinyAmmunitionTypeEnum,
    DestinyDamageTypeEnum,
    DestinyItemSubTypeEnum,
    DestinyWeaponSlotEnum,
)
from Backend.database.models import DiscordUsers
from Backend.networking.bungieApi import BungieApi
from NetworkingSchemas.destiny.weapons import DestinyWeaponModel, DestinyWeaponsModel


@dataclasses.dataclass
class DestinyWeapons:
    """Clan specific API calls"""

    db: AsyncSession
    user: Optional[DiscordUsers]

    def __post_init__(self):
        if self.user:
            # some shortcuts
            self.discord_id = self.user.discord_id
            self.destiny_id = self.user.destiny_id
            self.system = self.user.system

            # the network class
            self.api = BungieApi(db=self.db, user=self.user)

    @staticmethod
    async def get_all_weapons() -> DestinyWeaponsModel:
        """Return all weapons"""

        weapons = await destiny_items.get_all_weapons()

        # loop through the weapons and format them
        format_helper = {}
        for weapon in weapons:
            if weapon.name not in format_helper:
                format_helper.update(
                    {
                        weapon.name: DestinyWeaponModel(
                            name=weapon.name,
                            description=weapon.description,
                            flavor_text=weapon.flavor_text,
                            weapon_type=" ".join(
                                [
                                    part.capitalize()
                                    for part in DestinyItemSubTypeEnum(weapon.item_sub_type).name.split("_")
                                ]
                            ),
                            weapon_slot=" ".join(
                                [
                                    part.capitalize()
                                    for part in DestinyWeaponSlotEnum(weapon.bucket_type_hash).name.split("_")
                                ]
                            ),
                            damage_type=" ".join(
                                [
                                    part.capitalize()
                                    for part in DestinyDamageTypeEnum(weapon.default_damage_type).name.split("_")
                                ]
                            ),
                            ammo_type=" ".join(
                                [
                                    part.capitalize()
                                    for part in DestinyAmmunitionTypeEnum(weapon.ammo_type).name.split("_")
                                ]
                            ),
                            reference_ids=[weapon.reference_id],
                        )
                    }
                )
            else:
                format_helper[weapon.name].reference_ids.append(weapon.reference_id)

        return DestinyWeaponsModel(weapons=list[format_helper.values()])
