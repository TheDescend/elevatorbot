from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import Records


class CRUDRecords(CRUDBase):
    async def has_record(self, db: AsyncSession, destiny_id: int, triumph_hash: int) -> bool:
        """Return if the triumph is gotten (in the db)"""

        result: Optional[Records] = await self._get_with_key(db, (destiny_id, triumph_hash))

        # check if exists in db
        if not result:
            return False

        return result.completed

    async def get_record(self, db: AsyncSession, destiny_id: int, triumph_hash: int) -> Optional[Records]:
        """Return the db entry if exists"""

        return await self._get_with_key(db, (destiny_id, triumph_hash))

    async def update_record(self, db: AsyncSession, obj: Records, completed: bool):
        """Update the record entry in the db"""

        return await self._update(db, obj, completed=completed)

    async def insert_records(self, db: AsyncSession, objs: list[Records]):
        """Insert the record entries to the db"""

        return await self._mass_insert(db, objs)


records = CRUDRecords(Records)
