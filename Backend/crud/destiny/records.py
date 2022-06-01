from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import Records


class CRUDRecords(CRUDBase):
    async def has_record(self, db: AsyncSession, destiny_id: int, triumph_hash: int) -> bool:
        """Return if the triumph is gotten (in the db)"""

        result: Optional[Records] = await self.get_record(db=db, destiny_id=destiny_id, triumph_hash=triumph_hash)

        # check if exists in db
        return bool(result)

    async def gotten_records(self, db: AsyncSession, destiny_id: int) -> list[Records]:
        """Return all gotten records (in the db)"""

        results: list[Records] = await self._get_multi(db=db, destiny_id=destiny_id)
        return results

    async def get_record(self, db: AsyncSession, destiny_id: int, triumph_hash: int) -> Optional[Records]:
        """Return the db entry if exists"""

        return await self._get_with_key(db, (destiny_id, triumph_hash))

    async def insert_records(self, db: AsyncSession, objs: list[Records]):
        """Insert the record entries to the db"""

        return await self._mass_insert(db, objs)


records = CRUDRecords(Records)
