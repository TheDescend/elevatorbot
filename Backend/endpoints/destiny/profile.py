from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.dependencies import get_db_session
from Backend import crud
from Backend.schemas.destiny.profile import DestinyProfileModel
from Backend.schemas.empty import EmptyResponseModel


router = APIRouter(
    prefix="/profile",
    tags=["destiny", "profile"],
)


@router.get("/discord/{discord_id}", response_model=DestinyProfileModel)
async def discord_get(discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """ Return a users profile """

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    return DestinyProfileModel.from_orm(profile)


@router.get("/destiny/{destiny_id}", response_model=DestinyProfileModel)
async def destiny_get(destiny_id: int, db: AsyncSession = Depends(get_db_session)):
    """ Return a users profile """

    profile = await crud.discord_users.get_profile_from_destiny_id(db, destiny_id)
    return DestinyProfileModel.from_orm(profile)


@router.get("/delete/{discord_id}", response_model=EmptyResponseModel)
async def discord_delete(discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """ Delete a users profile """

    await crud.discord_users.delete_profile(db, discord_id)
    return EmptyResponseModel()
