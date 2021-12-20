from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import Roles
from Backend.misc.cache import cache
from NetworkingSchemas.destiny.roles import RoleDataModel, RoleModel


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
                        role_name=result.role_name,
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
                role_name=result.role_name,
                role_data=RoleDataModel.parse_obj(result.role_data),
            )

            self.cache.roles.update({role_id: role_obj})

        return self.cache.roles[role_id]

    async def create_role(self, db: AsyncSession, role: RoleModel):
        """Insert the new role"""

        db_role = Roles(
            role_id=role.role_id, guild_id=role.guild_id, role_name=role.role_name, role_data=role.role_data.dict()
        )
        await self._insert(db=db, to_create=db_role)

        # insert into cache
        await self._update_cache(db=db, role=db_role)

    async def update_role(self, db: AsyncSession, role: RoleModel):
        """Update a role"""

        db_role = await self._get_with_key(db=db, primary_key=role.role_id)
        if not db_role:
            raise CustomException("RoleNotExist")
        await self._update(db=db, to_update=db_role, role_name=role.role_name, role_data=role.role_data.dict())

        # insert into cache / update the cache
        await self._update_cache(db=db, role=db_role)

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

        # get the pydantic model
        pydantic_model = RoleModel(
            role_id=role.role_id,
            guild_id=role.guild_id,
            role_name=role.role_name,
            role_data=RoleDataModel.parse_obj(role.role_data),
        )

        self.cache.roles.update({pydantic_model.role_id: pydantic_model})
        await self.__update_guild_cache(db=db, guild_id=pydantic_model.guild_id)

    async def __update_guild_cache(self, db: AsyncSession, guild_id: int):
        """Update the guild role cache"""

        try:
            self.cache.guild_roles.pop(guild_id)
        except KeyError:
            pass
        await self.get_guild_roles(db=db, guild_id=guild_id)


crud_roles = CRUDRoles(Roles)
