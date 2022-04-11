from __future__ import annotations

import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from Shared.networkingSchemas.base import CustomBaseModel

if TYPE_CHECKING:
    from Backend.database import Roles


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

    class Config:
        orm_mode = True


class RequirementIntegerModel(CustomBaseModel):
    # the id of the collectible / record / role
    id: int

    # reverse this requirement - only people WITHOUT it get it
    inverse: bool = False

    class Config:
        orm_mode = True


class RoleDataUserModel(CustomBaseModel):
    require_activity_completions: list[str] = []
    require_collectibles: list[bool] = []
    require_records: list[bool] = []
    require_role_ids: list[bool] = []


class RoleModel(CustomBaseModel):
    role_id: int
    guild_id: int

    category: str

    # mark the role as acquirable, but reliant on removed content
    deprecated: bool

    # set whether the role can be earned
    acquirable: bool

    # list of activities
    require_activity_completions: list[RequirementActivityModel] = []
    # list of collectible hashes
    require_collectibles: list[RequirementIntegerModel] = []
    # list of record hashes
    require_records: list[RequirementIntegerModel] = []
    # list of discord role ids
    # todo changed behaviour - can't be inverse anymore -> change that everywhere
    # todo old: require_role_ids: list[RequirementIntegerModel] = []
    require_role_ids: list[int] = []

    replaced_by_role_id: Optional[int] = None

    @classmethod
    def from_sql_model(cls, db_model: Roles):
        """Convert SqlAlchemy's `Roles` to this model"""

        return cls(
            role_id=db_model.role_id,
            guild_id=db_model.guild_id,
            category=db_model.category,
            deprecated=db_model.deprecated,
            acquirable=db_model.acquirable,
            require_activity_completions=[
                RequirementActivityModel.from_orm(activity) for activity in db_model.require_activity_completions
            ],
            require_collectibles=[
                RequirementIntegerModel.from_orm(collectible) for collectible in db_model.require_collectibles
            ],
            require_records=[RequirementIntegerModel.from_orm(record) for record in db_model.require_records],
            require_role_ids=[role.role_id for role in db_model.require_roles],
            replaced_by_role_id=db_model.replaced_by_role.role_id if db_model.replaced_by_role else None,
        )


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
