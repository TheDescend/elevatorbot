import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from Backend.crud.base import CRUDBase
from Backend.database.models import (
    ActivitiesUsersWeapons,
    DestinyInventoryItemDefinition,
)
from DestinyEnums.enums import (
    DestinyDamageTypeEnum,
    DestinyItemSubTypeEnum,
    DestinyWeaponSlotEnum,
)
from NetworkingSchemas.destiny.weapons import DestinyTopWeaponsStatInputModelEnum


class CRUDWeapons(CRUDBase):
    async def get_usage(
        self,
        db: AsyncSession,
        weapon_ids: list[int],
        destiny_id: int,
        character_class: Optional[str] = None,
        character_ids: Optional[list[int]] = None,
        mode: Optional[int] = None,
        activity_hashes: Optional[list[int]] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
    ) -> list[ActivitiesUsersWeapons]:
        """Return where the specified weapon was used"""

        query = select(ActivitiesUsersWeapons)

        # filter by weapon ids
        query = query.filter(ActivitiesUsersWeapons.weapon_id.in_(weapon_ids))

        # filter by params
        query = self.filter_by_params(
            query=query,
            destiny_id=destiny_id,
            character_class=character_class,
            character_ids=character_ids,
            mode=mode,
            activity_hashes=activity_hashes,
            start_time=start_time,
            end_time=end_time,
        )

        result = await self._execute_query(db=db, query=query)
        return result.all()

    async def get_top(
        self,
        db: AsyncSession,
        slot: DestinyWeaponSlotEnum,
        stat: DestinyTopWeaponsStatInputModelEnum,
        destiny_id: int,
        weapon_type: Optional[DestinyItemSubTypeEnum] = None,
        damage_type: Optional[DestinyDamageTypeEnum] = None,
        character_class: Optional[str] = None,
        character_ids: Optional[list[int]] = None,
        mode: Optional[int] = None,
        activity_hashes: Optional[list[int]] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
    ) -> list[Row]:
        """Return the top weapons for the slot sorted by the input stat"""

        query = select(
            ActivitiesUsersWeapons.weapon_id,
            DestinyInventoryItemDefinition.name,
            DestinyInventoryItemDefinition.item_sub_type,
            DestinyInventoryItemDefinition.tier_type_name,
            DestinyInventoryItemDefinition.default_damage_type,
            DestinyInventoryItemDefinition.ammo_type,
            func.sum(ActivitiesUsersWeapons.unique_weapon_kills).label("kills"),
            func.sum(ActivitiesUsersWeapons.unique_weapon_precision_kills).label("precision_kills"),
        )

        # join the tables together
        query = query.filter(ActivitiesUsersWeapons.weapon_id == DestinyInventoryItemDefinition.reference_id)

        # make sure the slot is correct
        query = query.filter(DestinyInventoryItemDefinition.bucket_type_hash == slot.value)

        # filter by the weapon type
        if damage_type:
            query = query.filter(DestinyInventoryItemDefinition.default_damage_type == damage_type.value)

        # filter by the damage type
        if weapon_type:
            query = query.filter(DestinyInventoryItemDefinition.item_sub_type == weapon_type.value)

        # filter by params
        query = self.filter_by_params(
            query=query,
            destiny_id=destiny_id,
            character_class=character_class,
            character_ids=character_ids,
            mode=mode,
            activity_hashes=activity_hashes,
            start_time=start_time,
            end_time=end_time,
        )

        # sort by the given stat
        match stat:
            case stat.KILLS:
                query = query.order_by(func.sum(ActivitiesUsersWeapons.unique_weapon_kills).desc())
            case _:
                query = query.order_by(func.sum(ActivitiesUsersWeapons.unique_weapon_precision_kills).desc())

        result = await self._execute_query(db=db, query=query)
        return result.all()

    @staticmethod
    def filter_by_params(
        query: Select,
        destiny_id: int,
        character_class: Optional[str] = None,
        character_ids: Optional[list[int]] = None,
        mode: Optional[int] = None,
        activity_hashes: Optional[list[int]] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
    ) -> Select:
        """Filter by the params"""

        # filter by destiny id
        query = query.filter(ActivitiesUsersWeapons.user.destiny_id == destiny_id)

        # filter by character class
        if character_class:
            query = query.filter(ActivitiesUsersWeapons.user.character_class == character_class)

        # filter by character ids
        if character_ids:
            query = query.filter(ActivitiesUsersWeapons.user.character_id.in_(character_ids))

        # filter by mode
        if mode and not activity_hashes:
            query = query.filter(ActivitiesUsersWeapons.user.activity.modes.any(mode))

        # filter by character class
        if activity_hashes:
            query = query.filter(ActivitiesUsersWeapons.user.activity.director_activity_hash.in_(activity_hashes))

        # filter by start time
        if start_time:
            query = query.filter(ActivitiesUsersWeapons.user.activity.period >= start_time)

        # filter by end time
        if end_time:
            query = query.filter(ActivitiesUsersWeapons.user.activity.period <= end_time)

        return query


weapons = CRUDWeapons(ActivitiesUsersWeapons)
