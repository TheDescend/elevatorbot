from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import Versions


class CRUDVersions(CRUDBase):
    async def get(self, db: AsyncSession, name: str):
        """Gets the current version"""

        return self._get_with_key(db=db, primary_key=name)

    async def upsert(self, db: AsyncSession, name: str, version: str):
        """Upsert the version"""

        await self._upsert(db=db, model_data={"name": name, "version": version})


versions = CRUDVersions(Versions)
