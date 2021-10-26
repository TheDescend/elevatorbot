from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import destiny_manifest
from Backend.dependencies import get_db_session
from Backend.schemas.destiny.activities import DestinyActivitiesModel

router = APIRouter(
    prefix="/activities",
    tags=["destiny", "activities"],
)


@router.get("/get/all", response_model=DestinyActivitiesModel)
async def get_all(db: AsyncSession = Depends(get_db_session)):
    """Return all activities and their hashes"""

    return DestinyActivitiesModel(activities=await destiny_manifest.get_all_definitions(db=db))
