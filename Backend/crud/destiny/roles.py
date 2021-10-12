from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import Roles
from Backend.schemas.destiny.roles import RoleModel


class CRUDRoles(CRUDBase):
    async def get_guild_roles(self, db: AsyncSession, guild_id: int) -> list[Roles]:
        """Return all guild roles"""

        return await self._get_multi(db=db, guild_id=guild_id)

    async def get_role(self, db: AsyncSession, role_id: int) -> Roles:
        """Return the role by id"""

        return await self._get_with_key(db=db, primary_key=role_id)

    async def create_role(self, db: AsyncSession, role: RoleModel):
        """Insert the new role"""

        db_role = Roles(
            role_id=role.role_id, guild_id=role.guild_id, role_name=role.role_name, role_data=role.role_data.dict()
        )
        await self._insert(db=db, to_create=db_role)

    async def update_role(self, db: AsyncSession, role: RoleModel):
        """Update a role"""

        db_role = await self.get_role(db=db, role_id=role.role_id)
        await self._update(db=db, to_update=db_role, role_name=role.role_name, role_data=role.role_data.dict())

    async def delete_guild_roles(self, db: AsyncSession, guild_id: int):
        """Delete all guild roles"""

        # get all guild roles
        guild_roles: list[Roles] = await self._get_multi(db=db, guild_id=guild_id)

        # delete them
        for role in guild_roles:
            await self._delete(db=db, obj=role)

    async def delete_role(self, db: AsyncSession, role_id: int):
        """Delete a role"""

        await self._delete(db=db, primary_key=role_id)


roles = CRUDRoles(Roles)
