from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import Roles


class CRUDRoles(CRUDBase):
    async def upsert(self, db: AsyncSession, guild_id: int, role_name: str, role_id: int):
        """Upsert the role. role_name "Registered" and "Unregistered" have special behaviour and should not be used by user"""

        await self._upsert(db=db, model_data={"guild_id": guild_id, "role_name": role_name, "role_id": role_id})

    async def delete(self, db: AsyncSession, guild_id: int, role_id: int):
        """Delete the item(s)"""

        results = await self._get_multi(db, guild_id=guild_id, role_id=role_id)
        for result in results:
            await self._delete(db, obj=result)

    async def get(self, db: AsyncSession, guild_id: int, role_name: str) -> Optional[Roles]:
        """Get the role"""

        return await self._get_with_key(db=db, primary_key=(guild_id, role_name))

    async def get_registration_roles(self, db: AsyncSession) -> dict:
        """
        Get the Registered / Unregistered roles

        Returns: {
            guild_id: [
                Roles,
                ...
            ],
            ...
        }

        Note: There are a max of two entries in the return list for every guild (Registered / Unregistered)
        """

        query = select(Roles).filter(or_(Roles.role_name == "Registered", Roles.role_name == "Unregistered"))

        result = await self._execute_query(db=db, query=query)
        results: list[Roles] = result.scalars().fetchall()

        # format it like shown in docstring
        data = {}
        for result in results:
            try:
                data[result.guild_id].append(result)
            except KeyError:
                data.update({result.guild_id: [result]})
        return data

    async def get_all(self, db: AsyncSession, guild_id: int) -> list[Roles]:
        """Get all roles (except Registered / Unregistered)"""

        query = select(Roles).filter(
            Roles.guild_id == guild_id, Roles.role_name != "Registered", Roles.role_name != "Unregistered"
        )

        result = await self._execute_query(db=db, query=query)
        return result.scalars().fetchall()


roles = CRUDBase(Roles)
