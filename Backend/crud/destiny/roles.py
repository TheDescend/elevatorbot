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
                model = RoleModel(
                    role_id=result.role_id,
                    guild_id=result.guild_id,
                    role_data=RoleDataModel.parse_obj(result.role_data),
                )
                results.append(model)

                # also cache it
                self.cache.roles.update({model.role_id: model})

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

    async def create_role(self, db: AsyncSession, role: RoleModel):
        """Insert the new role"""

        self._check_role(role)

        db_role = Roles(role_id=role.role_id, guild_id=role.guild_id, role_data=role.role_data.dict())
        await self._insert(db=db, to_create=db_role)

        # insert into cache
        await self._update_cache(db=db, role=db_role)

    async def update_role(self, db: AsyncSession, role_id: int, role: RoleModel):
        """Update a role"""

        self._check_role(role)

        # check if the primary key changed
        if role.role_id != role_id:
            # delete old and insert
            await self.delete_role(db=db, role_id=role_id)
            await self.create_role(db=db, role=role)

        else:
            # update the role
            db_role = await self._get_with_key(db=db, primary_key=role_id)
            if not db_role:
                raise CustomException("Role does not exist")

            await self._update(db=db, to_update=db_role, role_id=role_id, role_data=role.role_data.dict())
            await self._update_cache(db=db, role=role)

    @staticmethod
    def _check_role(role: RoleModel):
        """Check that the roles are formatted ok"""

        # check that start time > end time
        for activity in role.role_data.require_activity_completions:
            for period in activity.allow_time_periods + activity.disallow_time_periods:
                if period.start_time >= period.end_time:
                    raise CustomException("End Time cannot be older than Start Time")

                if not period.start_time.tzinfo or not period.end_time.tzinfo:
                    raise CustomException("Naive datetimes are not supported")

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
