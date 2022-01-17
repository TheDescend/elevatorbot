import asyncio
import dataclasses
from typing import Optional

from anyio import create_task_group
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.profile import DestinyProfile
from Backend.core.errors import CustomException
from Backend.crud import crud_activities
from Backend.crud.destiny.roles import CRUDRoles, crud_roles
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

    db: AsyncSession
    user: DestinyProfile

    crud_roles: CRUDRoles = crud_roles

    _cache_worthy: dict = dataclasses.field(default_factory=dict, init=False)
    _cache_worthy_info: dict = dataclasses.field(default_factory=dict, init=False)

    async def get_missing_roles(self, guild_id: int) -> MissingRolesModel:
        """Return all the missing guild roles"""

        # get the users completion status
        user_roles = await self.get_guild_roles(guild_id=guild_id)
        missing_roles = user_roles.not_earned

        result = MissingRolesModel()

        # loop through the roles and sort them based on if they are acquirable or not
        for role_data in missing_roles:
            role = await self.crud_roles.get_role(db=self.db, role_id=role_data.discord_role_id)

            model = RolesCategoryModel(category=role.role_data.category, discord_role_id=role.role_id)

            # check if deprecated
            if role.role_data.deprecated:
                result.deprecated.append(model)
            else:
                result.acquirable.append(model)

        return result

    async def get_guild_roles(self, guild_id: int) -> EarnedRolesModel:
        """Return all the gotten / not gotten guild roles"""

        # get all guild roles
        guild_roles = await self.crud_roles.get_guild_roles(db=self.db, guild_id=guild_id)
        user_roles = EarnedRolesModel()

        # get them in anyio tasks
        async with create_task_group() as tg:
            for role in guild_roles:
                tg.start_soon(self._has_role, role, True, True)

        # loop through the roles now that the tasks are done and categorise them
        for role in guild_roles:
            category = str(role.role_data.category)
            model = RolesCategoryModel(category=category, discord_role_id=role.role_id)

            replaced_by_role_id = role.role_data.replaced_by_role_id

            if self._cache_worthy[role.role_id] == RoleEnum.EARNED:
                user_roles.earned.append(model)

            elif self._cache_worthy[role.role_id] == RoleEnum.NOT_EARNED:
                user_roles.not_earned.append(model)

            if replaced_by_role_id:
                if (
                    self._cache_worthy[role.role_id] == RoleEnum.EARNED
                    and self._cache_worthy[replaced_by_role_id] == RoleEnum.EARNED
                ):
                    user_roles.earned_but_replaced_by_higher_role.append(model)

                    # remove the old entry if exist
                    try:
                        user_roles.earned.remove(model)
                    except KeyError:
                        pass

        return user_roles

    async def has_role(self, role: RoleModel, i_only_need_the_bool: bool = False) -> EarnedRoleModel:
        """
        Return is the role is gotten and a dictionary of what is missing to get the role

        If the role is currently not acquirable, this returns RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE, None

        Argument `i_only_need_the_bool` makes this stop as soon as worthy is not true anymore
        """

        worthy, data = await self._has_role(
            role=role, called_with_task_group=False, i_only_need_the_bool=i_only_need_the_bool
        )
        return EarnedRoleModel(earned=worthy, role=role, user_role_data=data)

    async def _has_role(
        self, role: RoleModel, called_with_task_group: bool, i_only_need_the_bool: bool
    ) -> tuple[RoleEnum, Optional[RoleDataUserModel]]:
        """Check the role. Can be used in anyio task groups"""

        # check if it is set as acquirable
        if not role.role_data.acquirable:
            return RoleEnum.NOT_ACQUIRABLE, None

        # check cache first
        if role.role_id in self._cache_worthy:
            return self._cache_worthy[role.role_id], self._cache_worthy_info[role.role_id]

        # get all get_requirements in anyio tasks
        self._cache_worthy_info[role.role_id] = {}
        try:
            results: list[RoleEnum] = []
            async with create_task_group() as tg:
                for requirement_name, _ in role.role_data:
                    tg.start_soon(
                        self._check_requirements,
                        results,
                        role,
                        requirement_name,
                        i_only_need_the_bool,
                        called_with_task_group,
                    )

        except RoleNotEarnedException as e:
            self._cache_worthy[role.role_id] = RoleEnum.NOT_EARNED
            return self._cache_worthy[role.role_id], RoleDataUserModel.parse_obj(self._cache_worthy_info[e.role_id])

        # loop through the results and check if all reqs are OK
        worthy = RoleEnum.EARNED
        for result in results:
            if result == RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE and worthy == RoleEnum.EARNED:
                worthy = RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE
            elif result == RoleEnum.NOT_EARNED:
                worthy = RoleEnum.NOT_EARNED

        # put the results in the cache and return them
        self._cache_worthy[role.role_id] = worthy

        return self._cache_worthy[role.role_id], self._cache_worthy_info[role.role_id]

    async def _check_requirements(
        self,
        results: list[RoleEnum],
        role: RoleModel,
        requirement_name: str,
        i_only_need_the_bool: bool,
        called_with_task_group: bool,
    ):
        """Check the get_requirements. Can be used in task groups"""

        worthy = RoleEnum.EARNED

        match requirement_name:
            case "require_activity_completions":
                self._cache_worthy_info[role.role_id].update({"require_activity_completions": []})

                # loop through the activities
                for entry in role.role_data.require_activity_completions:
                    found = await crud_activities.get_activities(
                        db=self.db,
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

                    # todo better return the additional information like do you need a flawless -> link_to_role
                    link_to_activity = "www.google.com"
                    self._cache_worthy_info[role.role_id]["require_activity_completions"].append(
                        f"""{len(found)} / {entry.count} - [Details]({link_to_activity})"""
                    )

                    # make this end early
                    if i_only_need_the_bool and worthy == RoleEnum.NOT_EARNED:
                        raise RoleNotEarnedException(role_id=role.role_id)

                    # check if other processes ended negatively already
                    if role.role_id in self._cache_worthy:
                        break

            case "require_collectibles":
                self._cache_worthy_info[role.role_id].update({"require_collectibles": []})

                # loop through the collectibles
                for collectible in role.role_data.require_collectibles:
                    result = await self.user.has_collectible(collectible.id)

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

            case "require_records":
                self._cache_worthy_info[role.role_id].update({"require_records": []})

                # loop through the records
                for record in role.role_data.require_records:
                    result = await self.user.has_triumph(record.id)

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

            case "require_role_ids":
                self._cache_worthy_info[role.role_id].update({"require_role_ids": []})

                # loop through the role_ids
                for requirement_role in role.role_data.require_role_ids:
                    # alright so this is a bit more convoluted
                    # simply calling this function again would lead to double-checking / race conditions when checking all roles (because of task groups)
                    # but just waiting would not work too, since a single role can get checked too
                    # so, we are waiting if called with tasks groups, and looking ourselves if not
                    if called_with_task_group:
                        # 5 minutes wait time
                        waited_for = 0
                        while waited_for < 300:
                            if requirement_role.id in self._cache_worthy:

                                if self._cache_worthy[requirement_role.id] == RoleEnum.NOT_EARNED:
                                    if not requirement_role.inverse:
                                        worthy = RoleEnum.NOT_EARNED
                                        self._cache_worthy_info[role.role_id]["require_role_ids"].append(False)
                                    else:
                                        self._cache_worthy_info[role.role_id]["require_role_ids"].append(True)
                                else:
                                    if not requirement_role.inverse:
                                        self._cache_worthy_info[role.role_id]["require_role_ids"].append(True)
                                    else:
                                        worthy = RoleEnum.NOT_EARNED
                                        self._cache_worthy_info[role.role_id]["require_role_ids"].append(False)

                                break

                            waited_for += 2
                            await asyncio.sleep(2)

                        # this is only called if nothing was found
                        if waited_for >= 300:
                            raise CustomException("RoleLookupTimedOut")

                    # check the sub-roles ourselves
                    else:
                        sub_role: Roles = await crud_roles.get_role(db=self.db, role_id=requirement_role.id)
                        sub_role_worthy, _ = await self._has_role(
                            role=sub_role, called_with_task_group=False, i_only_need_the_bool=i_only_need_the_bool
                        )

                        if (
                            sub_role_worthy == RoleEnum.EARNED
                            or sub_role_worthy == RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE
                        ):
                            if not requirement_role.inverse:
                                self._cache_worthy_info[role.role_id]["require_role_ids"].append(True)
                            else:
                                worthy = RoleEnum.NOT_EARNED
                                self._cache_worthy_info[role.role_id]["require_role_ids"].append(False)

                        else:
                            if not requirement_role.inverse:
                                worthy = RoleEnum.NOT_EARNED
                                self._cache_worthy_info[role.role_id]["require_role_ids"].append(False)
                            else:
                                self._cache_worthy_info[role.role_id]["require_role_ids"].append(True)

                    # make this end early
                    if i_only_need_the_bool and worthy == RoleEnum.NOT_EARNED:
                        raise RoleNotEarnedException(role_id=role.role_id)

                    # check if other processes ended negatively already
                    if role.role_id in self._cache_worthy:
                        break

            case "replaced_by_role_id":
                # only need to check this sometimes
                if role.role_data.replaced_by_role_id and not called_with_task_group:
                    # check the higher role
                    higher_role: Roles = await crud_roles.get_role(
                        db=self.db, role_id=role.role_data.replaced_by_role_id
                    )
                    higher_role_worthy, _ = await self._has_role(
                        role=higher_role, called_with_task_group=False, i_only_need_the_bool=i_only_need_the_bool
                    )

                    if higher_role_worthy == RoleEnum.EARNED:
                        worthy = RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE

        results.append(worthy)
