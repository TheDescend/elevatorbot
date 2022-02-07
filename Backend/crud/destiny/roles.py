from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import Roles
from Backend.misc.cache import cache
from Shared.networkingSchemas.destiny.roles import RoleDataModel, RoleModel


class CRUDRoles(CRUDBase):
    cache = cache

    async def get_guild_roles(self, db: AsyncSession, guild_id: int) -> list[RoleModel]:
        """Return all guild roles"""

        # populate cache if not exists
        if guild_id not in self.cache.guild_roles:
            db_results = await self._get_multi(db=db, guild_id=guild_id)

            # format them
            results = []
            for result in db_results:
                results.append(
                    RoleModel(
                        role_id=result.role_id,
                        guild_id=result.guild_id,
                        role_data=RoleDataModel.parse_obj(result.role_data),
                    )
                )

            self.cache.guild_roles.update({guild_id: results})

        return self.cache.guild_roles[guild_id]

    async def get_role(self, db: AsyncSession, role_id: int) -> RoleModel:
        """Return the role by id"""

        # populate cache if not exists
        if role_id not in self.cache.roles:
            result = await self._get_with_key(db=db, primary_key=role_id)
            if not result:
                raise CustomException("RoleNotExist")

            role_obj = RoleModel(
                role_id=result.role_id,
                guild_id=result.guild_id,
                role_data=RoleDataModel.parse_obj(result.role_data),
            )

            self.cache.roles.update({role_id: role_obj})

        return self.cache.roles[role_id]

    async def upsert_role(self, db: AsyncSession, role: RoleModel):
        """Upsert a role"""

        await self._upsert(db=db, model_data=role.dict())

        # insert into cache / update the cache
        await self._update_cache(db=db, role=role)

    async def delete_guild_roles(self, db: AsyncSession, guild_id: int):
        """Delete all guild roles"""

        # get all guild roles
        guild_roles: list[Roles] = await self._get_multi(db=db, guild_id=guild_id)

        # delete them
        for role in guild_roles:
            await self._delete(db=db, obj=role)
            try:
                self.cache.roles.pop(role.role_id)
            except KeyError:
                pass

        # delete from cache
        await self.__update_guild_cache(db=db, guild_id=guild_id)

    async def delete_role(self, db: AsyncSession, role_id: int):
        """Delete a role"""

        obj = await self._delete(db=db, primary_key=role_id)

        # delete from cache
        try:
            self.cache.roles.pop(role_id)
        except KeyError:
            pass
        if obj:
            await self.__update_guild_cache(db=db, guild_id=obj.guild_id)

    async def _update_cache(self, db: AsyncSession, role: RoleModel):
        """Update the role cache"""

        self.cache.roles.update({role.role_id: role})
        await self.__update_guild_cache(db=db, guild_id=role.guild_id)

    async def __update_guild_cache(self, db: AsyncSession, guild_id: int):
        """Update the guild role cache"""

        try:
            self.cache.guild_roles.pop(guild_id)
        except KeyError:
            pass
        await self.get_guild_roles(db=db, guild_id=guild_id)


crud_roles = CRUDRoles(Roles)
