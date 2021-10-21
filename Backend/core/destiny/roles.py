import asyncio
import dataclasses
from enum import Enum
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.profile import DestinyProfile
from Backend.core.errors import CustomException
from Backend.crud import activities
from Backend.crud.destiny.roles import CRUDRoles, roles
from Backend.database.models import Roles
from Backend.schemas.destiny.roles import (
    EarnedRoleModel,
    EarnedRolesModel,
    MissingRolesModel,
)


class RoleEnum(Enum):
    NOT_ACQUIRABLE = 0
    EARNED = 10
    EARNED_BUT_REPLACED_BY_HIGHER_ROLE = 20
    NOT_EARNED = 30


@dataclasses.dataclass
class UserRoles:
    """Check for role completions with a cache to remove double role check on role dependencies"""

    db: AsyncSession
    user: DestinyProfile

    roles: CRUDRoles = roles

    _cache_worthy: dict = dataclasses.field(default_factory=dict, init=False)
    _cache_worthy_info: dict = dataclasses.field(default_factory=dict, init=False)


    async def get_missing_roles(self, guild_id: int) -> MissingRolesModel:
        """Return all the missing guild roles"""

        # get the users completion status
        user_roles = await self.get_guild_roles(guild_id=guild_id)
        missing_roles = user_roles.not_earned

        result = MissingRolesModel()

        # loop through the roles and sort them based on if they are acquirable or not
        for category, role_ids in missing_roles.items():
            # loop through the roles
            for role_id in role_ids:
                role = await self.roles.get_role(db=self.db, role_id=role_id)

                # check if deprecated
                if role.role_data["deprecated"]:
                    if category not in result.deprecated:
                        result.deprecated.update({category: []})
                    result.deprecated["category"].append(role_id)

                else:
                    if category not in result.acquirable:
                        result.acquirable.update({category: []})
                    result.acquirable["category"].append(role_id)

        return result


    async def get_guild_roles(self, guild_id: int) -> EarnedRolesModel:
        """Return all the gotten / not gotten guild roles"""

        # get all guild roles
        guild_roles = await self.roles.get_guild_roles(db=self.db, guild_id=guild_id)
        user_roles = EarnedRolesModel()

        # gather the results for faster responses
        await asyncio.gather(
            *[
                self._has_role(role=role, called_with_asyncio_gather=True, i_only_need_the_bool=True)
                for role in guild_roles
            ]
        )

        # loop through the roles now that the gather is done and categorise them
        for role in guild_roles:
            replaced_by_role_id = role.role_data["replaced_by_role_id"]

            if self._cache_worthy[role.role_id] == RoleEnum.EARNED:
                category = str(role.role_data["category"])
                if category not in user_roles.earned:
                    user_roles.earned.update({category: []})

                user_roles.earned[category].append(role.role_id)

            elif self._cache_worthy[role.role_id] == RoleEnum.NOT_EARNED:
                category = str(role.role_data["category"])
                if category not in user_roles.not_earned:
                    user_roles.not_earned.update({category: []})

                user_roles.not_earned[category].append(role.role_id)

            if replaced_by_role_id:
                if self._cache_worthy[role.role_id] == RoleEnum.EARNED and self._cache_worthy[replaced_by_role_id] == RoleEnum.EARNED:
                    category = str(role.role_data["category"])
                    if category not in user_roles.earned_but_replaced_by_higher_role:
                        user_roles.earned_but_replaced_by_higher_role.update({category: []})

                    user_roles.earned_but_replaced_by_higher_role[category].append(role.role_id)

                    # remove the old entry if exist
                    try:
                        user_roles.earned[category].pop(role.role_id)
                    except KeyError:
                        pass

        return user_roles


    async def has_role(self, role: Roles, i_only_need_the_bool: bool = False) -> EarnedRoleModel:
        """
        Return is the role is gotten and a dictionary of what is missing to get the role

        If the role is currently not acquirable, this returns RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE, None

        Argument `i_only_need_the_bool` makes this stop as soon as worthy is not true anymore
        """

        worthy, data = await self._has_role(role=role, called_with_asyncio_gather=False, i_only_need_the_bool=i_only_need_the_bool)
        return EarnedRoleModel(earned=worthy, user_data=data, role_data=role.role_data)


    async def _has_role(self, role: Roles, called_with_asyncio_gather: bool, i_only_need_the_bool: bool) -> tuple[RoleEnum, Optional[dict]]:
        """Check the role. Can be asyncio.gather()'d"""

        # check if it is set as acquirable
        if not role.role_data["acquirable"]:
            return RoleEnum.NOT_ACQUIRABLE, None

        # check cache first
        if role.role_id in self._cache_worthy:
            return self._cache_worthy[role.role_id], self._cache_worthy_info[role.role_id]

        # gather all get_requirements
        results = await asyncio.gather(
            *[
                self._check_requirements(
                    role=role,
                    requirement_name=requirement_name,
                    requirement_value=requirement_value,
                    i_only_need_the_bool=i_only_need_the_bool,
                    called_with_asyncio_gather=called_with_asyncio_gather
                )
                for requirement_name, requirement_value in role.role_data.items()
            ]
        )

        # check cache again to catch not-worthy's
        if role.role_id in self._cache_worthy:
            return self._cache_worthy[role.role_id], self._cache_worthy_info[role.role_id]

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
        self, role: Roles, requirement_name: str, requirement_value: Any, i_only_need_the_bool: bool, called_with_asyncio_gather: bool
    ) -> RoleEnum:
        """Check the get_requirements. Can be asyncio.gather()'d"""

        worthy = RoleEnum.EARNED

        match requirement_name:
            case "require_activity_completions":
                self._cache_worthy_info[role.role_id].update(
                    {
                        "require_activity_completions": []
                    }
                )

                # loop through the activities
                for entry in requirement_value:
                    found = await activities.get_activities(
                        db=self.db,
                        activity_hashes=entry["allowed_activity_hashes"],
                        no_checkpoints=not entry["allow_checkpoints"],
                        require_team_flawless=entry["require_team_flawless"],
                        require_individual_flawless=entry["require_individual_flawless"],
                        require_score=entry["require_score"],
                        require_kills=entry["require_kills"],
                        require_kills_per_minute=entry["require_kills_per_minute"],
                        require_kda=entry["require_kda"],
                        require_kd=entry["require_kd"],
                        maximum_allowed_players=entry["maximum_allowed_players"],
                        allow_time_periods=entry["allow_time_periods"],
                        disallow_time_periods=entry["disallow_time_periods"],
                    )

                    # todo make sure this can be viewed on a website nicely. Maybe even put a link there
                    # check how many activities fulfill that
                    if len(found) < entry["count"]:
                        worthy = RoleEnum.NOT_EARNED

                    self._cache_worthy_info[role.role_id]["require_activity_completions"].append(f"""{len(found)} / {entry["count"]}""")

                    # make this end early
                    if i_only_need_the_bool and worthy == RoleEnum.NOT_EARNED:
                        # put the results in the cache and return them
                        self._cache_worthy[role.role_id] = worthy

                        return self._cache_worthy[role.role_id]

                    # check if other processes ended negatively already
                    if role.role_id in self._cache_worthy:
                        break

            case "require_collectibles":
                self._cache_worthy_info[role.role_id].update(
                    {
                        "require_collectibles": []
                    }
                )

                # loop through the collectibles
                for collectible in requirement_value:
                    result = await self.user.has_collectible(collectible)

                    if not result:
                        worthy = RoleEnum.NOT_EARNED

                    self._cache_worthy_info[role.role_id]["require_collectibles"].append(result)

                    # make this end early
                    if i_only_need_the_bool and worthy == RoleEnum.NOT_EARNED:
                        # put the results in the cache and return them
                        self._cache_worthy[role.role_id] = worthy

                        return self._cache_worthy[role.role_id]

                    # check if other processes ended negatively already
                    if role.role_id in self._cache_worthy:
                        break

            case "require_records":
                self._cache_worthy_info[role.role_id].update(
                    {
                        "require_records": []
                    }
                )

                # loop through the records
                for record in requirement_value:
                    result = await self.user.has_triumph(record)

                    if not result:
                        worthy = RoleEnum.NOT_EARNED

                    self._cache_worthy_info[role.role_id]["require_records"].append(result)

                    # make this end early
                    if i_only_need_the_bool and worthy == RoleEnum.NOT_EARNED:
                        # put the results in the cache and return them
                        self._cache_worthy[role.role_id] = worthy

                        return self._cache_worthy[role.role_id]

                    # check if other processes ended negatively already
                    if role.role_id in self._cache_worthy:
                        break

            case "require_role_ids":
                self._cache_worthy_info[role.role_id].update(
                    {
                        "require_role_ids": []
                    }
                )

                # loop through the role_ids
                for role_id in requirement_value:
                    # alright so this is a bit more convoluted
                    # simply calling this function again would lead to double checking / race conditions when checking all roles (because of .gather())
                    # but just waiting would not work too, since a single role can get checked too
                    # so we are waiting if called with gather, and looking ourselves if not
                    if called_with_asyncio_gather:
                        # 5 minutes wait time
                        waited_for = 0
                        while waited_for < 300:
                            if role_id in self._cache_worthy:

                                if self._cache_worthy[role_id] == RoleEnum.NOT_EARNED:
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
                        sub_role: Roles = await roles.get_role(db=self.db, role_id=role_id)
                        sub_role_worthy, _ = await self._has_role(role=sub_role, called_with_asyncio_gather=False, i_only_need_the_bool=i_only_need_the_bool)

                        if sub_role_worthy == RoleEnum.EARNED or sub_role_worthy == RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE:
                            self._cache_worthy_info[role.role_id]["require_role_ids"].append(True)

                        else:
                            worthy = RoleEnum.NOT_EARNED
                            self._cache_worthy_info[role.role_id]["require_role_ids"].append(False)

                    # make this end early
                    if i_only_need_the_bool and worthy == RoleEnum.NOT_EARNED:
                        # put the results in the cache and return them
                        self._cache_worthy[role.role_id] = worthy

                        return self._cache_worthy[role.role_id]

                    # check if other processes ended negatively already
                    if role.role_id in self._cache_worthy:
                        break

            case "replaced_by_role_id":
                # only need to check this sometimes
                if requirement_value and not called_with_asyncio_gather:
                    # check the higher role
                    higher_role: Roles = await roles.get_role(db=self.db, role_id=requirement_value)
                    higher_role_worthy, _ = await self._has_role(role=higher_role, called_with_asyncio_gather=False, i_only_need_the_bool=i_only_need_the_bool)

                    if higher_role_worthy == RoleEnum.EARNED:
                        worthy = RoleEnum.EARNED_BUT_REPLACED_BY_HIGHER_ROLE

        return worthy
