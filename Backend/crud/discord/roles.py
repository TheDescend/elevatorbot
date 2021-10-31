from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import Roles


class CRUDRoles(CRUDBase):
    async def upsert(self, db: AsyncSession, guild_id: int, role_name: str, role_id: int):
        """Upsert the role"""

        await self._upsert(db=db, model_data={"guild_id": guild_id, "role_name": role_name, "role_id": role_id})

    async def delete(self, db: AsyncSession, guild_id: int, role_id: int):
        """Delete the item(s)"""

        results = await self._get_multi(db, guild_id=guild_id, role_id=role_id)
        for result in results:
            await self._delete(db, obj=result)

    async def get(self, db: AsyncSession, guild_id: int, role_name: str) -> Optional[Roles]:
        """Get the role"""

        return await self._get_with_key(db=db, primary_key=(guild_id, role_name))

    async def get_all(self, db: AsyncSession, guild_id: int) -> list[Roles]:
        """Get all roles"""

        query = select(Roles).filter(Roles.guild_id == guild_id)

        result = await self._execute_query(db=db, query=query)
        return result.scalars().fetchall()


roles = CRUDBase(Roles)
