from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import DestinyInventoryItemDefinition


class CRUDDestinyItems(CRUDBase):
    async def get_all_weapons(self, db: AsyncSession) -> list[DestinyInventoryItemDefinition]:
        """Return all weapons"""

        # item_type == 3 -> weapons
        return await self._get_multi(db=db, item_type=3)

    async def get_item(self, db: AsyncSession, item_id: int) -> Optional[DestinyInventoryItemDefinition]:
        """Return the item"""

        return await self._get_with_key(db=db, primary_key=item_id)


destiny_items = CRUDDestinyItems(DestinyInventoryItemDefinition)
