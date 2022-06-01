from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import Collectibles


class CRUDCollectibles(CRUDBase):
    async def has_collectible(self, db: AsyncSession, destiny_id: int, collectible_hash: int) -> bool:
        """Return if the collectible is gotten (in the db)"""

        result: Optional[Collectibles] = await self.get_collectible(
            db=db, destiny_id=destiny_id, collectible_hash=collectible_hash
        )

        # check if exists in db
        return bool(result)

    async def gotten_collectibles(self, db: AsyncSession, destiny_id: int) -> list[Collectibles]:
        """Return all gotten collectibles (in the db)"""

        results: list[Collectibles] = await self._get_multi(db=db, destiny_id=destiny_id)
        return results

    async def get_collectible(self, db: AsyncSession, destiny_id: int, collectible_hash: int) -> Optional[Collectibles]:
        """Return the db entry if exists"""

        return await self._get_with_key(db, (destiny_id, collectible_hash))

    async def insert_collectibles(self, db: AsyncSession, objs: list[Collectibles]):
        """Insert the collectible entries in the db"""

        await self._mass_insert(db, objs)


collectibles = CRUDCollectibles(Collectibles)
