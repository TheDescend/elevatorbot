from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend import crud
from Backend.core.destiny.activities import DestinyActivities
from Backend.core.destiny.profile import DestinyProfile
from Backend.crud import destiny_manifest
from Backend.dependencies import get_db_session
from Backend.schemas.destiny.activities import (
    DestinyActivitiesModel,
    DestinyActivityDetailsModel,
    DestinyLastInputModel,
)

router = APIRouter(
    prefix="/activities",
    tags=["destiny", "activities"],
)


@router.get("/get/all", response_model=DestinyActivitiesModel)
async def get_all(db: AsyncSession = Depends(get_db_session)):
    """Return all activities and their hashes"""

    return DestinyActivitiesModel(activities=await destiny_manifest.get_all_definitions(db=db))


@router.get("/{guild_id}/{discord_id}/last", response_model=DestinyActivityDetailsModel)
async def last(
    guild_id: int, discord_id: int, time_input: DestinyLastInputModel, db: AsyncSession = Depends(get_db_session)
):
    """Return information about the last completed activity"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)

    # update the users db entries
    activities = DestinyActivities(db=db, user=user)
    await activities.update_activity_db()

    return await activities.get_last_played(
        mode=time_input.mode if time_input.mode else 0,
        activity_ids=time_input.activity_ids,
        character_class=time_input.character_class,
        completed=time_input.completed,
    )
