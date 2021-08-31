from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import Collectibles


class CRUDCollectibles(CRUDBase):
    async def has_collectible(self, db: AsyncSession, destiny_id: int, collectible_hash: int) -> bool:
        """Return if the collectible is gotten (in the db)"""

        result: Optional[Collectibles] = await self._get_with_key(db, (destiny_id, collectible_hash))

        # check if exists in db
        if not result:
            return False

        return result.owned

    async def get_collectible(self, db: AsyncSession, destiny_id: int, collectible_hash: int) -> Optional[Collectibles]:
        """Return the db entry if exists"""

        return await self._get_with_key(db, (destiny_id, collectible_hash))

    async def update_collectible(self, db: AsyncSession, obj: Collectibles, owned: bool):
        """Update the collectible entry in the db"""

        return await self._update(db, obj, owned=owned)

    async def insert_collectibles(self, db: AsyncSession, objs: list[Collectibles]):
        """Insert the collectible entries in the db"""

        return await self._mass_insert(db, objs)


collectibles = CRUDCollectibles(Collectibles)
