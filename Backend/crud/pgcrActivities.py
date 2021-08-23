from Backend.crud.base import CRUDBase
from Backend.database.models import (
    PgcrActivitiesFailToGet,
    PgcrActivitiesUsersStat,
    PgcrActivitiesUsersStatsWeapon,
    PgcrActivity,
)


class CRUDActivitiesFailToGet(CRUDBase):
    pass


class CRUDActivities(CRUDBase):
    pass


class CRUDActivitiesUsersStats(CRUDBase):
    pass


class CRUDActivitiesUsersStatsWeapons(CRUDBase):
    pass


activities_fail_to_get = CRUDActivitiesFailToGet(PgcrActivitiesFailToGet)
activities = CRUDActivities(PgcrActivity)
activities_users_stats = CRUDActivitiesUsersStats(PgcrActivitiesUsersStat)
activities_users_stats_weapons = CRUDActivitiesUsersStatsWeapons(
    PgcrActivitiesUsersStatsWeapon
)
