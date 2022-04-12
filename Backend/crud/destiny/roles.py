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

        # get the relationships
        relationships = await self._get_role_relationships(db=db, role=role)

        db_role = Roles(
            role_id=role.role_id,
            guild_id=role.guild_id,
            category=role.category,
            deprecated=role.deprecated,
            acquirable=role.acquirable,
            **relationships,
        )

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

        # get the relationships
        relationships = await self._get_role_relationships(db=db, role=role, db_role=db_role)

        # update the role
        await self._update(
            db=db,
            to_update=db_role,
            role_id=role.role_id,
            guild_id=role.guild_id,
            category=role.category,
            deprecated=role.deprecated,
            acquirable=role.acquirable,
            **relationships,
        )

        # update guild roles and roles cache
        await self._update_guild_cache(db=db, guild_id=role.guild_id)

    async def _get_role_relationships(self, db: AsyncSession, role: RoleModel, db_role: Roles | None = None) -> dict:
        """Get the role relationships as a dict. Used by both insert and update"""

        # delete old items
        if db_role:
            for activity in db_role.requirement_require_activity_completions:
                await self._delete(db=db, obj=activity)
            for collectible in db_role.requirement_require_collectibles:
                await self._delete(db=db, obj=collectible)
            for record in db_role.requirement_require_records:
                await self._delete(db=db, obj=record)

        to_update = {
            "requirement_require_activity_completions": [],
            "requirement_require_collectibles": [],
            "requirement_require_records": [],
            "requirement_replaced_by_role": None,
        }

        for activity in role.require_activity_completions:
            to_update["requirement_require_activity_completions"].append(
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

        for collectible in role.require_collectibles:
            to_update["requirement_require_collectibles"].append(
                RolesInteger(
                    bungie_id=collectible.bungie_id,
                    inverse=collectible.inverse,
                )
            )

        for record in role.require_records:
            to_update["requirement_require_records"].append(
                RolesInteger(
                    bungie_id=record.bungie_id,
                    inverse=record.inverse,
                )
            )

        # we do not want to return this dict on an update call, because it will try to re-add them to the association table -> integrity error
        if not db_role:
            to_update.update({"requirement_require_roles": []})
            existing_roles = []
        else:
            existing_roles = db_role.requirement_require_roles

        # add new ones
        for require_role_id in role.require_role_ids:
            if require_role_id not in existing_roles:
                # get the role from the db
                require_role = await self._get_one(db=db, role_id=require_role_id)
                if not require_role:
                    raise CustomException("RoleNotExist")

                if not db_role:
                    to_update["requirement_require_roles"].append(require_role)
                else:
                    db_role.requirement_require_roles.append(require_role)

        # remove old roles
        if db_role:
            for old_require_role in db_role.requirement_require_roles:
                if old_require_role.role_id not in role.require_role_ids:
                    db_role.requirement_require_roles.remove(old_require_role)

        if role.replaced_by_role_id:
            # get the role from the db
            replacement_role = await self._get_one(db=db, role_id=role.replaced_by_role_id)
            if not replacement_role:
                raise CustomException("RoleNotExist")

            to_update["requirement_replaced_by_role"] = replacement_role

        return to_update

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

        # get the role
        db_role: Roles = await self._get_one(db=db, role_id=role_id)

        # delete it
        await self._delete(db=db, obj=db_role)

        # delete from cache
        try:
            self.cache.roles.pop(role_id)
        except KeyError:
            pass
        if db_role:
            # update guild roles and roles cache
            await self._update_guild_cache(db=db, guild_id=db_role.guild_id)

    async def _update_guild_cache(self, db: AsyncSession, guild_id: int):
        """Update the guild role cache"""

        try:
            self.cache.guild_roles.pop(guild_id)
        except KeyError:
            pass
        await self.get_guild_roles(db=db, guild_id=guild_id)


crud_roles = CRUDRoles(Roles)
