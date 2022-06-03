from fastapi import APIRouter

from Backend.core.destiny.activities import DestinyActivities
from Backend.crud import destiny_manifest, discord_users
from Backend.database import acquire_db_session
from Shared.networkingSchemas.destiny import (
    DestinyActivitiesModel,
    DestinyActivityDetailsModel,
    DestinyActivityInputModel,
    DestinyActivityOutputModel,
    DestinyLastInputModel,
)

router = APIRouter(
    prefix="/destiny/activities",
    tags=["destiny", "activities"],
)


@router.get("/get/all", response_model=DestinyActivitiesModel)  # has test
async def get_all():
    """Return all activities and their hashes"""

    async with acquire_db_session() as db:
        return DestinyActivitiesModel(activities=await destiny_manifest.get_all_activities(db=db))


@router.post("/{guild_id}/{discord_id}/last", response_model=DestinyActivityDetailsModel)  # has test
async def last(guild_id: int, discord_id: int, last_input: DestinyLastInputModel):
    """Return information about the last completed activity"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)

        # update the user's db entries
        activities = DestinyActivities(db=db, user=user)
        await activities.update_activity_db()

        return await activities.get_last_played(
            mode=last_input.mode if last_input.mode else 0,
            activity_ids=last_input.activity_ids,
            character_class=last_input.character_class,
            completed=last_input.completed,
        )


@router.post("/{guild_id}/{discord_id}/activity", response_model=DestinyActivityOutputModel)  # has test
async def activity(
    guild_id: int,
    discord_id: int,
    activity_input: DestinyActivityInputModel,
):
    """Return information about the user their stats in the supplied activity ids"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)

        # update the user's db entries
        activities = DestinyActivities(db=db, user=user)
        await activities.update_activity_db()

        return await activities.get_activity_stats(
            activity_ids=activity_input.activity_ids,
            mode=activity_input.mode,
            character_class=activity_input.character_class,
            character_ids=activity_input.character_ids,
            start_time=activity_input.start_time,
            end_time=activity_input.end_time,
        )


@router.get("/get/grandmaster", response_model=DestinyActivitiesModel)  # has test
async def grandmaster():
    """Return information about all grandmaster nfs from the DB"""

    async with acquire_db_session() as db:
        return DestinyActivitiesModel(activities=await destiny_manifest.get_grandmaster_nfs(db=db))
