import dataclasses
import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud import activities, weapons
from Backend.crud.destiny.items import destiny_items
from Backend.database.enums import (
    DestinyAmmunitionTypeEnum,
    DestinyDamageTypeEnum,
    DestinyItemSubTypeEnum,
    DestinyWeaponSlotEnum,
)
from Backend.database.models import DiscordUsers
from Backend.networking.bungieApi import BungieApi
from NetworkingSchemas.destiny.weapons import (
    DestinyWeaponModel,
    DestinyWeaponsModel,
    DestinyWeaponStatsModel,
)


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

    async def get_all_weapons(self) -> DestinyWeaponsModel:
        """Return all weapons"""

        weapons = await destiny_items.get_all_weapons(db=self.db)

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

    async def get_weapon_stats(
        self,
        weapon_ids: list[int],
        character_class: Optional[str] = None,
        character_ids: Optional[list[int]] = None,
        mode: Optional[int] = None,
        activity_hashes: Optional[list[int]] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
    ) -> DestinyWeaponStatsModel:
        """
        Return the stats for the given weapon.
        A weapon can have multiple ids, due to sunsetting. That's why the arg is a list
        """

        usages = await weapons.get_usage(
            db=self.db,
            weapon_ids=weapon_ids,
            destiny_id=self.destiny_id,
            character_class=character_class,
            character_ids=character_ids,
            mode=mode,
            activity_hashes=activity_hashes,
            start_time=start_time,
            end_time=end_time,
        )

        result = DestinyWeaponStatsModel(
            total_kills=0,
            total_precision_kills=0,
            total_activities=0,
            best_kills=0,
            best_kills_activity_name="",
            best_kills_activity_id=0,
            best_kills_date=datetime.datetime.min,
        )

        if not usages:
            raise CustomException("WeaponUnused")

        # loop through all the usages and find what we are looking for
        for usage in usages:
            result.total_kills += usage.unique_weapon_kills
            result.total_precision_kills += usage.unique_weapon_precision_kills
            result.total_activities += 1

            if usage.unique_weapon_kills > result.best_kills:
                result.best_kills = usage.unique_weapon_kills
                result.best_kills_activity_name = str(usage.user.activity.reference_id)
                result.best_kills_activity_id = usage.user.activity.instance_id
                result.best_kills_date = usage.user.activity.period

        # change the reference id of the best activity to the actual name
        result.best_kills_activity_name = await activities.get_activity_name(
            db=self.db, activity_id=int(result.best_kills_activity_name)
        )

        return result
