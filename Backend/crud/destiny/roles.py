import copy

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import Roles, RolesActivity, RolesActivityTimePeriod, RolesInteger
from Backend.misc.cache import cache
from Shared.networkingSchemas.destiny.roles import RoleModel


class CRUDRoles(CRUDBase):
    cache = cache

    async def get_guild_roles(self, db: AsyncSession, guild_id: int) -> list[Roles]:
        """Return all guild roles"""

        # populate cache if not exists
        if guild_id not in self.cache.guild_roles:
            db_results = await self._get_multi(db=db, guild_id=guild_id)

            # format them
            results: list[Roles] = []
            for result in db_results:
                # copy it once to prevent it from expiring
                role_obj = copy.copy(result)
                results.append(role_obj)

                # also cache it
                self.cache.roles.update({role_obj.role_id: role_obj})

            self.cache.guild_roles.update({guild_id: results})

        return self.cache.guild_roles[guild_id]

    async def get_role(self, db: AsyncSession, role_id: int) -> Roles:
        """Return the role by id"""

        # populate cache if not exists
        if role_id not in self.cache.roles:
            result = await self._get_one(db=db, role_id=role_id)
            if not result:
                raise CustomException("RoleNotExist")

            # copy it once to prevent it from expiring
            role_obj = copy.copy(result)

            self.cache.roles.update({role_id: role_obj})

        return self.cache.roles[role_id]

    async def create_role(self, db: AsyncSession, role: RoleModel):
        """Insert the new role"""

        self._check_role(role)

        db_role = Roles(
            role_id=role.role_id,
            guild_id=role.guild_id,
            category=role.category,
            deprecated=role.deprecated,
            acquirable=role.acquirable,
            replaced_by_role_id=role.replaced_by_role_id,
        )

        # set the relationships
        await self._set_role_relationships(db=db, role=role, db_role=db_role)

        await self._insert(db=db, to_create=db_role)

        # update guild roles and roles cache
        await self._update_guild_cache(db=db, guild_id=role.guild_id)

    async def update_role(self, db: AsyncSession, role_id: int, role: RoleModel):
        """Update a role"""

        self._check_role(role)

        # update the role
        db_role: Roles = await self._get_one(db=db, role_id=role_id)
        if not db_role:
            raise CustomException("Role does not exist")

        # set the relationship to null to delete orphans
        db_role = await self._update(
            db=db,
            to_update=db_role,
            role_id=role.role_id,
            guild_id=role.guild_id,
            category=role.category,
            deprecated=role.deprecated,
            acquirable=role.acquirable,
            replaced_by_role_id=role.replaced_by_role_id,
            require_activity_completions=[],
            require_collectibles=[],
            require_records=[],
            require_roles=[],
        )

        # set the relationships
        await self._set_role_relationships(db=db, role=role, db_role=db_role)

        # flush changes
        await db.flush()

        # update guild roles and roles cache
        await self._update_guild_cache(db=db, guild_id=role.guild_id)

    async def _set_role_relationships(self, db: AsyncSession, role: RoleModel, db_role: Roles):
        """Set the role relationships. Used by both insert and update"""

        # insert new ones
        for activity in role.require_activity_completions:
            db_role.require_activity_completions.append(
                RolesActivity(
                    allowed_activity_hashes=activity.allowed_activity_hashes,
                    count=activity.count,
                    allow_checkpoints=activity.allow_checkpoints,
                    require_team_flawless=activity.require_team_flawless,
                    require_individual_flawless=activity.require_individual_flawless,
                    require_score=activity.require_score,
                    require_kills=activity.require_kills,
                    require_kills_per_minute=activity.require_kills_per_minute,
                    require_kda=activity.require_kda,
                    require_kd=activity.require_kd,
                    maximum_allowed_players=activity.maximum_allowed_players,
                    allow_time_periods=[
                        RolesActivityTimePeriod(
                            start_time=time_period.start_time,
                            end_time=time_period.end_time,
                        )
                        for time_period in activity.allow_time_periods
                    ],
                    disallow_time_periods=[
                        RolesActivityTimePeriod(
                            start_time=time_period.start_time,
                            end_time=time_period.end_time,
                        )
                        for time_period in activity.disallow_time_periods
                    ],
                    inverse=activity.inverse,
                )
            )

        # insert new ones
        for collectible in role.require_collectibles:
            db_role.require_collectibles.append(
                RolesInteger(
                    id=collectible.id,
                    inverse=collectible.inverse,
                )
            )

        # insert new ones
        for record in role.require_records:
            db_role.require_records.append(
                RolesInteger(
                    id=record.id,
                    inverse=record.inverse,
                )
            )

        # don't delete old roles, that would be a bad idea. We just overwrite them
        # insert new ones
        for require_role_id in role.require_role_ids:
            # get the role from the db
            require_role = await self._get_one(db=db, role_id=require_role_id)
            if not require_role:
                raise CustomException("RoleNotExist")

            db_role.require_roles.append(require_role)

    @staticmethod
    def _check_role(role: RoleModel):
        """Check that the roles are formatted ok"""

        # check that start time > end time
        for activity in role.require_activity_completions:
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

        # update guild roles and roles cache
        await self._update_guild_cache(db=db, guild_id=guild_id)

    async def delete_role(self, db: AsyncSession, role_id: int):
        """Delete a role"""

        obj = await self._delete(db=db, primary_key=role_id)

        # delete from cache
        try:
            self.cache.roles.pop(role_id)
        except KeyError:
            pass
        if obj:
            # update guild roles and roles cache
            await self._update_guild_cache(db=db, guild_id=obj.guild_id)

    async def _update_guild_cache(self, db: AsyncSession, guild_id: int):
        """Update the guild role cache"""

        try:
            self.cache.guild_roles.pop(guild_id)
        except KeyError:
            pass
        await self.get_guild_roles(db=db, guild_id=guild_id)


crud_roles = CRUDRoles(Roles)
