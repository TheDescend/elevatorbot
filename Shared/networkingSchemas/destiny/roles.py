import datetime
from enum import Enum
from typing import Optional

from Shared.networkingSchemas.base import CustomBaseModel


class RolesCategoryModel(CustomBaseModel):
    category: str
    discord_role_id: int


class EarnedRolesModel(CustomBaseModel):
    earned: list[RolesCategoryModel] = []
    earned_but_replaced_by_higher_role: list[RolesCategoryModel] = []
    not_earned: list[RolesCategoryModel] = []


class MissingRolesModel(CustomBaseModel):
    acquirable: list[RolesCategoryModel] = []
    deprecated: list[RolesCategoryModel] = []


class TimePeriodModel(CustomBaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime


class RequirementActivityModel(CustomBaseModel):
    # which activities are allowed
    allowed_activity_hashes: list[int]

    # how many times the activities need to be cleared
    count: int

    # should only fresh runs count
    allow_checkpoints: bool = False

    # do the runs need to be flawless
    require_team_flawless: bool = False
    require_individual_flawless: bool = False

    # do some other get_requirements need to be fulfilled
    require_score: Optional[int] = None
    require_kills: Optional[int] = None
    require_kills_per_minute: Optional[float] = None
    require_kda: Optional[float] = None
    require_kd: Optional[float] = None

    # does it need to be a lowman
    maximum_allowed_players: int = 6

    # allow / disallow time periods
    allow_time_periods: list[TimePeriodModel] = []
    disallow_time_periods: list[TimePeriodModel] = []

    # reverse this requirement - only people WITHOUT it get it
    inverse: bool = False


class RequirementIntegerModel(CustomBaseModel):
    # the id of the collectible / record / role
    id: int

    # reverse this requirement - only people WITHOUT it get it
    inverse: bool = False


class RoleDataModel(CustomBaseModel):
    # the category of the role. Used to better format roles
    category: str = "Destiny Roles"

    # mark the role as acquirable, but reliant on removed content
    deprecated: bool = False

    # set whether the role can be earned
    acquirable: bool = True

    require_activity_completions: list[RequirementActivityModel] = []
    require_collectibles: list[RequirementIntegerModel] = []
    require_records: list[RequirementIntegerModel] = []
    require_role_ids: list[RequirementIntegerModel] = []

    replaced_by_role_id: Optional[int] = None


class RoleDataUserModel(CustomBaseModel):
    require_activity_completions: list[str]
    require_collectibles: list[bool]
    require_records: list[bool]
    require_role_ids: list[bool]


class RoleModel(CustomBaseModel):
    role_id: int
    guild_id: int
    role_name: str
    role_data: RoleDataModel


class RolesModel(CustomBaseModel):
    roles: list[RoleModel] = []


class RoleEnum(Enum):
    NOT_ACQUIRABLE = "Not currently acquirable"
    EARNED = "Earned"
    EARNED_BUT_REPLACED_BY_HIGHER_ROLE = "Earned, but replaced by higher role"
    NOT_EARNED = "Not Earned"


class EarnedRoleModel(CustomBaseModel):
    earned: RoleEnum
    role: RoleModel
    user_role_data: Optional[RoleDataUserModel] = None
