import datetime

from pydantic import BaseModel


class EarnedRolesModel(BaseModel):
    """
    Format:

    {
        "category_name": list[role_ids]
    }
    """

    earned: dict[str, list[int]] = {}
    earned_but_replaced_by_higher_role: dict[str, list[int]] = {}
    not_earned: dict[str, list[int]] = {}


class EarnedRoleModel(BaseModel):
    earned: bool
    data: dict


class TimePeriodModel(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime


class ActivityModel(BaseModel):
    # which activities are allowed
    allowed_activity_hashes: list[int]

    # how many times the activities need to be cleared
    count: int

    # should only fresh runs count
    allow_checkpoints: bool = False

    # do the runs need to be flawless
    require_team_flawless: bool = False
    require_individual_flawless: bool = False

    # do some other requirements need to be fulfilled
    require_score: int = None
    require_kills: int = None
    require_kills_per_minute: float = None
    require_kda: float = None
    require_kd: float = None

    # does it need to be a lowman
    maximum_allowed_players: int = 6

    # allow / disallow time periods
    allow_time_periods: list[TimePeriodModel] = []
    disallow_time_periods: list[TimePeriodModel] = []


class RoleDataModel(BaseModel):
    # the category of the role. Used to better format roles
    category: str = None

    # mark the role as acquirable, but reliant on removed content
    deprecated: bool = False

    # set whether the role can be earned
    acquirable: bool = True

    require_activity_completions: list[ActivityModel] = []

    require_collectibles: list[int] = []
    require_records: list[int] = []

    require_role_ids: list[int] = []
    replaced_by_role_id: int = None


class RoleModel(BaseModel):
    role_id: int
    guild_id: int
    role_name: str
    role_data: RoleDataModel


class RolesModel(BaseModel):
    roles: list[RoleModel] = []
