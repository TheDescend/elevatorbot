from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.crud.cache import cache
from Backend.database.models import Roles
from NetworkingSchemas.destiny.roles import RoleModel


class CRUDRoles(CRUDBase):
    cache = cache

    async def get_guild_roles(self, db: AsyncSession, guild_id: int) -> list[Roles]:
        """Return all guild roles"""

        # populate cache if not exists
        if guild_id not in self.cache.guild_roles:
            self.cache.guild_roles.update({guild_id: await self._get_multi(db=db, guild_id=guild_id)})

        return self.cache.guild_roles[guild_id]

    async def get_role(self, db: AsyncSession, role_id: int) -> Roles:
        """Return the role by id"""

        # populate cache if not exists
        if role_id not in self.cache.roles:
            self.cache.roles.update({role_id: await self._get_with_key(db=db, primary_key=role_id)})

        return self.cache.roles[role_id]

    async def create_role(self, db: AsyncSession, role: RoleModel):
        """Insert the new role"""

        # todo validate that the role_data is valid

        db_role = Roles(
            role_id=role.role_id, guild_id=role.guild_id, role_name=role.role_name, role_data=role.role_data.dict()
        )
        await self._insert(db=db, to_create=db_role)

        # insert into cache
        self.cache.roles.update({role.role_id: db_role})

    async def update_role(self, db: AsyncSession, role: RoleModel):
        """Update a role"""

        # todo validate that the role_data is valid

        db_role = await self.get_role(db=db, role_id=role.role_id)
        await self._update(db=db, to_update=db_role, role_name=role.role_name, role_data=role.role_data.dict())

        # insert into cache / update the cache
        self.cache.roles.update({role.role_id: db_role})

    async def delete_guild_roles(self, db: AsyncSession, guild_id: int):
        """Delete all guild roles"""

        # get all guild roles
        guild_roles: list[Roles] = await self._get_multi(db=db, guild_id=guild_id)

        # delete them
        for role in guild_roles:
            await self._delete(db=db, obj=role)

        # delete from cache
        try:
            self.cache.guild_roles.pop(guild_id)
        except KeyError:
            pass

    async def delete_role(self, db: AsyncSession, role_id: int):
        """Delete a role"""

        await self._delete(db=db, primary_key=role_id)

        # delete from cache
        try:
            self.cache.roles.pop(role_id)
        except KeyError:
            pass


roles = CRUDRoles(Roles)
