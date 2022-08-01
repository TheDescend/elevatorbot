import datetime
from typing import Optional

from bungio.models import DamageType, DestinyItemSubType
from sqlalchemy import func, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from Backend.bungio.manifest import destiny_manifest
from Backend.crud.base import CRUDBase
from Backend.database.models import Activities, ActivitiesUsers, ActivitiesUsersWeapons
from Shared.enums.destiny import DestinyWeaponSlotEnum
from Shared.networkingSchemas.destiny import DestinyTopWeaponsStatInputModelEnum


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
        query = query.join(ActivitiesUsers)
        query = query.join(Activities)

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
        return result.scalars().all()

    async def get_top(
        self,
        db: AsyncSession,
        slot: DestinyWeaponSlotEnum,
        stat: DestinyTopWeaponsStatInputModelEnum,
        destiny_id: int,
        weapon_type: Optional[DestinyItemSubType] = None,
        damage_type: Optional[DamageType] = None,
        character_class: Optional[str] = None,
        character_ids: Optional[list[int]] = None,
        mode: Optional[int] = None,
        activity_hashes: Optional[list[int]] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
    ) -> list[Row]:
        """Return the top weapons for the slot sorted by the input stat"""

        # which weapons are okay?
        allowed_weapon_ids: set[int] = set()
        weapons = await destiny_manifest.get_all_weapons()
        for _, weapon in weapons.items():
            # filter by weapon slot
            if weapon.inventory.bucket_type_hash != slot.value:
                continue

            # filter by the weapon type
            if weapon_type and weapon.item_sub_type != weapon_type:
                continue

            # filter by the damage type
            if damage_type and weapon.default_damage_type != damage_type:
                continue

            allowed_weapon_ids.add(weapon.hash)

        # do the db request
        query = select(
            ActivitiesUsersWeapons.weapon_id,
            func.sum(ActivitiesUsersWeapons.unique_weapon_kills).label("kills"),
            func.sum(ActivitiesUsersWeapons.unique_weapon_precision_kills).label("precision_kills"),
        )

        # join the tables together
        query = query.join(ActivitiesUsers)
        query = query.join(Activities)

        # group them
        query = query.group_by(ActivitiesUsersWeapons.weapon_id)

        # filter by weapon
        query = query.filter(ActivitiesUsersWeapons.weapon_id.in_(allowed_weapon_ids))

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
                query = query.order_by(func.sum(ActivitiesUsersWeapons.unique_weapon_kills).desc())  # noqa
            case _:
                query = query.order_by(func.sum(ActivitiesUsersWeapons.unique_weapon_precision_kills).desc())  # noqa

        result = await self._execute_query(db=db, query=query)  # noqa
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
        query = query.filter(ActivitiesUsers.destiny_id == destiny_id)

        # filter by character class
        if character_class:
            query = query.filter(ActivitiesUsers.character_class == character_class)

        # filter by character ids
        if character_ids:
            query = query.filter(ActivitiesUsers.character_id.in_(character_ids))

        # filter by mode
        if mode and not activity_hashes:
            query = query.filter(Activities.modes.any(mode))

        # filter by character class
        if activity_hashes:
            query = query.filter(Activities.director_activity_hash.in_(activity_hashes))

        # filter by start time
        if start_time:
            query = query.filter(Activities.period >= start_time)

        # filter by end time
        if end_time:
            query = query.filter(Activities.period <= end_time)

        return query


crud_weapons = CRUDWeapons(ActivitiesUsersWeapons)
