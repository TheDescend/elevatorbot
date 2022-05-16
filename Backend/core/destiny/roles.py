import asyncio
import dataclasses

from anyio import create_task_group
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.profile import DestinyProfile
from Backend.core.errors import CustomException
from Backend.crud import crud_activities
from Backend.crud.destiny.roles import CRUDRoles, crud_roles
from Backend.database.base import acquire_db_session
from Backend.database.models import Roles
from Shared.networkingSchemas.destiny.roles import (
    EarnedRoleModel,
    EarnedRolesModel,
    MissingRolesModel,
    RoleDataUserModel,
    RoleEnum,
    RoleModel,
    RolesCategoryModel,
)


class RoleNotEarnedException(Exception):
    """This is raised should a role not be earned and we don't want additional info"""

    def __init__(self, role_id: int):
        self.role_id = role_id


@dataclasses.dataclass
class UserRoles:
    """Check for role completions with a cache to remove double role check on role dependencies"""

    user: DestinyProfile

    crud_roles: CRUDRoles = crud_roles

    _cache_worthy: dict = dataclasses.field(default_factory=dict, init=False)
    _cache_worthy_info: dict = dataclasses.field(default_factory=dict, init=False)

    async def get_missing_roles(self, guild_id: int, db: AsyncSession) -> MissingRolesModel:
        """Return all the missing guild roles"""

        # get the users completion status
        user_roles = await self.get_guild_roles(guild_id=guild_id)
        missing_roles = user_roles.not_earned

        result = MissingRolesModel()

        # loop through the roles and sort them based on if they are acquirable or not
        for role_data in missing_roles:
            role = await self.crud_roles.get_role(db=db, role_id=role_data.discord_role_id)

            model = RolesCategoryModel(category=role.category, discord_role_id=role.role_id)

            # check if deprecated
            if role.deprecated:
                result.deprecated.append(model)
            else:
                result.acquirable.append(model)

        return result

    async def get_guild_roles(self, guild_id: int) -> EarnedRolesModel:
        """Return all the gotten / not gotten guild roles"""

        # get all guild roles
        async with acquire_db_session() as db:
            guild_roles = await self.crud_roles.get_guild_roles(db=db, guild_id=guild_id)
        user_roles = EarnedRolesModel()

        # get them in anyio tasks
        async with create_task_group() as tg:
            for role in guild_roles:
                tg.start_soon(lambda: self._has_role(role=role, called_with_task_group=True, i_only_need_the_bool=True))

        # loop through the roles now that the tasks are done and categorise them
        for role in guild_roles:
            category = str(role.category)
            model = RolesCategoryModel(category=category, discord_role_id=role.role_id)

            if self._cache_worthy[role.role_id] == RoleEnum.EARNED:
                user_roles.earned.append(model)

            elif self._cache_worthy[role.role_id] == RoleEnum.NOT_EARNED:
                user_roles.not_earned.append(model)

            if role.requirement_replaced_by_role:
                if (
                    self._cache_worthy[role.role_id] == RoleEnum.EARNED
                    and self._cache_worthy[role.requirement_replaced_by_role.role_id] == RoleEnum.EARNED
                ):
                    user_roles.earned_but_replaced_by_higher_role.append(model)

                    # remove the old entry if exist
                    try:
                        user_roles.earned.remove(model)
                    except KeyError:
                        pass

        return user_roles

    async def has_role(self, role: Roles, i_only_need_the_bool: bool = False) -> EarnedRoleModel:
        """
        Return is the role is gotten and a dictionary of what is missing to get the role

        If the role is currently not acquirable, this returns RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE, None

        Argument `i_only_need_the_bool` makes this stop as soon as worthy is not true anymore
        """

        worthy = await self._has_role(
            role=role, called_with_task_group=False, i_only_need_the_bool=i_only_need_the_bool
        )
        return EarnedRoleModel(
            earned=worthy,
            role=RoleModel.from_sql_model(role),
            user_role_data=RoleDataUserModel.parse_obj(self._cache_worthy_info[role.role_id]),
        )

    async def _has_role(self, role: Roles, called_with_task_group: bool, i_only_need_the_bool: bool) -> RoleEnum:
        """Check the role. Can be used in anyio task groups"""

        self._cache_worthy_info[role.role_id] = {}

        # check if it is set as acquirable
        if not role.acquirable:
            self._cache_worthy[role.role_id] = RoleEnum.NOT_ACQUIRABLE
            return RoleEnum.NOT_ACQUIRABLE

        # check cache first
        if role.role_id in self._cache_worthy:
            return self._cache_worthy[role.role_id]

        # get all get_requirements in anyio tasks
        try:
            results: list[RoleEnum] = []
            async with create_task_group() as tg:
                for requirement_name in role.__dict__:
                    # skip internals
                    if requirement_name.startswith("requirement_"):
                        tg.start_soon(
                            lambda: self.check_requirement(
                                results=results,
                                role=role,
                                requirement_name=requirement_name,
                                i_only_need_the_bool=i_only_need_the_bool,
                                called_with_task_group=called_with_task_group,
                            )
                        )

        except RoleNotEarnedException:
            self._cache_worthy[role.role_id] = RoleEnum.NOT_EARNED
            return self._cache_worthy[role.role_id]

        # loop through the results and check if all reqs are OK
        worthy = RoleEnum.EARNED
        for result in results:
            if result == RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE and worthy == RoleEnum.EARNED:
                worthy = RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE
            elif result == RoleEnum.NOT_EARNED:
                worthy = RoleEnum.NOT_EARNED

        # put the results in the cache and return them
        self._cache_worthy[role.role_id] = worthy

        return self._cache_worthy[role.role_id]

    async def check_requirement(
        self,
        results: list[RoleEnum],
        role: Roles,
        requirement_name: str,
        i_only_need_the_bool: bool,
        called_with_task_group: bool,
    ):
        """Check the get_requirements. Can be used in task groups"""

        worthy = RoleEnum.EARNED

        match requirement_name:
            case "requirement_require_activity_completions":
                self._cache_worthy_info[role.role_id].update({"require_activity_completions": []})

                # loop through the activities
                async with acquire_db_session() as db:
                    for entry in role.requirement_require_activity_completions:
                        found = await crud_activities.get_activities(
                            db=db,
                            destiny_id=self.user.destiny_id,
                            activity_hashes=entry.allowed_activity_hashes,
                            no_checkpoints=not entry.allow_checkpoints,
                            require_team_flawless=entry.require_team_flawless,
                            require_individual_flawless=entry.require_individual_flawless,
                            require_score=entry.require_score,
                            require_kills=entry.require_kills,
                            require_kills_per_minute=entry.require_kills_per_minute,
                            require_kda=entry.require_kda,
                            require_kd=entry.require_kd,
                            maximum_allowed_players=entry.maximum_allowed_players,
                            allow_time_periods=entry.allow_time_periods,
                            disallow_time_periods=entry.disallow_time_periods,
                        )

                        # check how many activities fulfill that
                        if len(found) < entry.count:
                            if not entry.inverse:
                                worthy = RoleEnum.NOT_EARNED

                        else:
                            if entry.inverse:
                                worthy = RoleEnum.NOT_EARNED

                        self._cache_worthy_info[role.role_id]["require_activity_completions"].append(
                            f"{len(found)} / {entry.count}"
                        )

                        # make this end early
                        if i_only_need_the_bool and worthy == RoleEnum.NOT_EARNED:
                            raise RoleNotEarnedException(role_id=role.role_id)

                        # check if other processes ended negatively already
                        if role.role_id in self._cache_worthy:
                            break

            case "requirement_require_collectibles":
                self._cache_worthy_info[role.role_id].update({"require_collectibles": []})

                # loop through the collectibles
                for collectible in role.requirement_require_collectibles:
                    result = await self.user.has_collectible(collectible.bungie_id)

                    if not result:
                        if not collectible.inverse:
                            worthy = RoleEnum.NOT_EARNED
                    else:
                        if collectible.inverse:
                            worthy = RoleEnum.NOT_EARNED

                    self._cache_worthy_info[role.role_id]["require_collectibles"].append(result)

                    # make this end early
                    if i_only_need_the_bool and worthy == RoleEnum.NOT_EARNED:
                        raise RoleNotEarnedException(role_id=role.role_id)

                    # check if other processes ended negatively already
                    if role.role_id in self._cache_worthy:
                        break

            case "requirement_require_records":
                self._cache_worthy_info[role.role_id].update({"require_records": []})

                # loop through the records
                for record in role.requirement_require_records:
                    result = await self.user.has_triumph(triumph_hash=record.bungie_id)

                    if not result:
                        if not record.inverse:
                            worthy = RoleEnum.NOT_EARNED
                    else:
                        if record.inverse:
                            worthy = RoleEnum.NOT_EARNED

                    self._cache_worthy_info[role.role_id]["require_records"].append(result.bool)

                    # make this end early
                    if i_only_need_the_bool and worthy == RoleEnum.NOT_EARNED:
                        raise RoleNotEarnedException(role_id=role.role_id)

                    # check if other processes ended negatively already
                    if role.role_id in self._cache_worthy:
                        break

            case "requirement_require_roles":
                self._cache_worthy_info[role.role_id].update({"require_role_ids": []})

                # loop through the role_ids
                for requirement_role in role.requirement_require_roles:
                    # get the role with the proper relationship depths from cache -> all attrs are loaded
                    async with acquire_db_session() as db:
                        requirement_role = await crud_roles.get_role(db=db, role_id=requirement_role.role_id)

                    # alright so this is a bit more convoluted
                    # simply calling this function again would lead to double-checking / race conditions when checking all roles (because of task groups)
                    # but just waiting would not work too, since a single role can get checked too
                    # so, we are waiting if called with tasks groups, and looking ourselves if not
                    if called_with_task_group:
                        # 5 minutes wait time
                        waited_for = 0
                        while waited_for < 300:
                            if requirement_role.role_id in self._cache_worthy:
                                if self._cache_worthy[requirement_role.role_id] == RoleEnum.NOT_EARNED:
                                    worthy = RoleEnum.NOT_EARNED
                                    self._cache_worthy_info[role.role_id]["require_role_ids"].append(False)
                                else:
                                    self._cache_worthy_info[role.role_id]["require_role_ids"].append(True)

                                break

                            waited_for += 2
                            await asyncio.sleep(2)

                        # this is only called if nothing was found
                        if waited_for >= 300:
                            raise CustomException("RoleLookupTimedOut")

                    # check the sub-roles ourselves
                    else:
                        sub_role_worthy = await self._has_role(
                            role=requirement_role,
                            called_with_task_group=False,
                            i_only_need_the_bool=i_only_need_the_bool,
                        )

                        # check if this role replaces the sub role
                        if (
                            requirement_role.requirement_replaced_by_role
                            and requirement_role.requirement_replaced_by_role.role_id == role.role_id
                        ):
                            # do not set it to EARNED
                            if sub_role_worthy == RoleEnum.EARNED:
                                sub_role_worthy = RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE
                                self._cache_worthy[requirement_role.role_id] = sub_role_worthy

                        if (
                            sub_role_worthy == RoleEnum.EARNED
                            or sub_role_worthy == RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE
                        ):
                            self._cache_worthy_info[role.role_id]["require_role_ids"].append(True)

                        else:
                            worthy = RoleEnum.NOT_EARNED
                            self._cache_worthy_info[role.role_id]["require_role_ids"].append(False)

                    # make this end early
                    if i_only_need_the_bool and worthy == RoleEnum.NOT_EARNED:
                        raise RoleNotEarnedException(role_id=role.role_id)

                    # check if other processes ended negatively already
                    if role.role_id in self._cache_worthy:
                        break

            case "requirement_replaced_by_role":
                # only need to check this sometimes
                if role.requirement_replaced_by_role and not called_with_task_group:
                    # get the role with the proper relationship depths -> all attrs are loaded
                    async with acquire_db_session() as db:
                        replaced_by_role = await crud_roles.get_role(
                            db=db, role_id=role.requirement_replaced_by_role.role_id
                        )

                    # edge case:
                    # the higher role requires this role, in that instance we do not check
                    # we instead check that on the higher role and change the RoleEnum for this
                    if role.role_id not in [
                        req_role.role_id for req_role in replaced_by_role.requirement_require_roles
                    ]:
                        # check the higher role
                        higher_role_worthy = await self._has_role(
                            role=replaced_by_role,
                            called_with_task_group=False,
                            i_only_need_the_bool=i_only_need_the_bool,
                        )

                        if higher_role_worthy == RoleEnum.EARNED:
                            worthy = RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE

        results.append(worthy)
