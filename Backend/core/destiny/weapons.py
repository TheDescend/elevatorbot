import dataclasses
import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud import activities, weapons
from Backend.crud.destiny.items import destiny_items
from Backend.database.models import DiscordUsers
from Backend.networking.bungieApi import BungieApi
from NetworkingSchemas.destiny.weapons import (
    DestinyTopWeaponModel,
    DestinyTopWeaponsModel,
    DestinyTopWeaponsStatInputModelEnum,
    DestinyWeaponModel,
    DestinyWeaponsModel,
    DestinyWeaponStatsModel,
)
from NetworkingSchemas.enums import (
    DestinyAmmunitionTypeEnum,
    DestinyDamageTypeEnum,
    DestinyItemSubTypeEnum,
    DestinyWeaponSlotEnum,
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

    async def get_top_weapons(
        self,
        stat: DestinyTopWeaponsStatInputModelEnum,
        how_many_per_slot: int,
        include_weapon_with_ids: list[int] = None,
        weapon_type: Optional[DestinyItemSubTypeEnum] = None,
        damage_type: Optional[DestinyDamageTypeEnum] = None,
        character_class: Optional[str] = None,
        character_ids: Optional[list[int]] = None,
        mode: Optional[int] = None,
        activity_hashes: Optional[list[int]] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
    ) -> DestinyTopWeaponsModel:
        """
        Return the top x weapons for every slot. include_weapon_with_ids is always included no matter what
        A weapon can have multiple ids, due to sunsetting. That's why the arg is a list
        """

        # get information about the sought weapon
        sought_weapon = None
        if include_weapon_with_ids:
            sought_weapon = await destiny_items.get_item(db=self.db, item_id=include_weapon_with_ids[0])

            # check if the weapon / damage type matches
            if sought_weapon.item_sub_type != weapon_type.value:
                raise CustomException("WeaponTypeMismatch")
            if sought_weapon.default_damage_type != damage_type.value:
                raise CustomException("WeaponDamageTypeMismatch")

        # loop through all three slots
        result = DestinyTopWeaponsModel()
        for slot in DestinyWeaponSlotEnum:
            # query the db

            top_weapons = await weapons.get_top(
                db=self.db,
                slot=slot,
                stat=stat,
                destiny_id=self.destiny_id,
                weapon_type=weapon_type,
                damage_type=damage_type,
                character_class=character_class,
                character_ids=character_ids,
                mode=mode,
                activity_hashes=activity_hashes,
                start_time=start_time,
                end_time=end_time,
            )

            # sort the weapons. This is needed because some weapons are reissued and have multiple ids
            to_sort = {}
            for weapon in top_weapons:
                # get the stat value
                stat_value = getattr(weapon, stat.name.lower())

                # insert into the sorting thing
                if weapon.name not in to_sort:
                    to_sort.update(
                        {
                            weapon.name: DestinyTopWeaponModel(
                                ranking=0,  # temp value
                                stat_value=stat_value,
                                weapon_ids=[weapon.weapon_id],
                                weapon_name=weapon.name,
                                weapon_type=" ".join(
                                    part.capitalize()
                                    for part in DestinyItemSubTypeEnum(weapon.item_sub_type).name.split("_")
                                ),
                                weapon_tier=weapon.tier_type_name,
                                weapon_damage_type=" ".join(
                                    part.capitalize()
                                    for part in DestinyDamageTypeEnum(weapon.default_damage_type).name.split("_")
                                ),
                                weapon_ammo_type=" ".join(
                                    part.capitalize()
                                    for part in DestinyAmmunitionTypeEnum(weapon.ammo_type).name.split("_")
                                ),
                            )
                        }
                    )

                # append the id and add the stat
                else:
                    to_sort[weapon.name].stat_value += stat_value
                    to_sort[weapon.name].weapon_ids.append(weapon.weapon_id)

            # sort the items
            sorted_slot: list[DestinyTopWeaponModel] = sorted(
                to_sort.values(), key=lambda entry: entry.stat_value, reverse=True
            )

            # set the rankings and the limit and include the sought weapon
            i = 0
            found = sought_weapon.bucket_type_hash == slot.value if sought_weapon else True
            final_slot = []
            for item in sorted_slot:
                i += 1

                if i <= how_many_per_slot:
                    item.ranking = i
                    final_slot.append(item)

                    if include_weapon_with_ids[0] in item.weapon_ids:
                        found = True

                elif not found:
                    if include_weapon_with_ids[0] in item.weapon_ids:
                        item.ranking = i
                        final_slot.append(item)
                        found = True

                else:
                    break

            # raise an error since the weapon wasn't found
            if not found:
                raise CustomException("WeaponUnused")

            # update the result
            setattr(result, slot.name.lower(), sorted_slot)

        return result
