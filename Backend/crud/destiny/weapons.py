import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import Activities, ActivitiesUsersWeapons, RssFeedItem


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

        query = select(ActivitiesUsersWeapons.unique_weapon_kills, ActivitiesUsersWeapons.unique_weapon_precision_kills)

        # filter by weapon ids
        query = query.filter(ActivitiesUsersWeapons.weapon_id.in_(weapon_ids))

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

        result = await self._execute_query(db=db, query=query)
        return result.scalars().all()


weapons = CRUDWeapons(ActivitiesUsersWeapons)
