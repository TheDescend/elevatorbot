from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.crud.cache import cache
from Backend.database.models import (
    DestinyCollectibleDefinition,
    DestinyInventoryItemDefinition,
    DestinyRecordDefinition,
)


class CRUDDestinyItems(CRUDBase):
    async def get_all_weapons(self, db: AsyncSession) -> list[DestinyInventoryItemDefinition]:
        """Return all weapons"""

        # item_type == 3 -> weapons
        return await self._get_multi(db=db, item_type=3)

    async def get_item(self, db: AsyncSession, item_id: int) -> Optional[DestinyInventoryItemDefinition]:
        """Return the item"""

        # check cache
        if item_id not in cache.items:
            cache.items.update({item_id: await self._get_with_key(db=db, primary_key=item_id)})

        return cache.items[item_id]

    async def get_collectible(self, db: AsyncSession, collectible_id: int) -> Optional[DestinyCollectibleDefinition]:
        """Return the collectible"""

        query = select(DestinyCollectibleDefinition)
        query = query.filter(DestinyCollectibleDefinition.reference_id == collectible_id)

        results = await self._execute_query(db=db, query=query)
        return results.scalar()

    async def get_record(self, db: AsyncSession, record_id: int) -> Optional[DestinyRecordDefinition]:
        """Return the record"""

        query = select(DestinyRecordDefinition)
        query = query.filter(DestinyRecordDefinition.reference_id == record_id)

        results = await self._execute_query(db=db, query=query)
        return results.scalar()

    async def get_catalysts(self, db: AsyncSession) -> list[DestinyRecordDefinition]:
        """Returns a list of the current catalysts"""

        query = select(DestinyRecordDefinition)
        query = query.filter(DestinyRecordDefinition.name.like(f"% Catalyst"))

        results = await self._execute_query(db=db, query=query)
        return results.scalars().all()


destiny_items = CRUDDestinyItems(DestinyInventoryItemDefinition)
