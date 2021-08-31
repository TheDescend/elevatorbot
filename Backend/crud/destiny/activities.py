from Backend.crud.base import CRUDBase
from Backend.database.models import (
    ActivitiesFailToGet,
    Activities,
    ActivitiesUsersStats,
    ActivitiesUsersStatsWeapons,
)


class CRUDActivitiesFailToGet(CRUDBase):
    pass


class CRUDActivities(CRUDBase):
    pass


class CRUDActivitiesUsersStats(CRUDBase):
    pass


class CRUDActivitiesUsersStatsWeapons(CRUDBase):
    pass


activities_fail_to_get = CRUDActivitiesFailToGet(ActivitiesFailToGet)
activities = CRUDActivities(Activities)
activities_users_stats = CRUDActivitiesUsersStats(ActivitiesUsersStats)
activities_users_stats_weapons = CRUDActivitiesUsersStatsWeapons(ActivitiesUsersStatsWeapons)
