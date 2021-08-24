from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.dependencies import get_db_session
from Backend import crud
from Backend.schemas.destiny.profile import DestinyJoinIdModel, DestinyProfileModel
from Backend.schemas.empty import EmptyResponseModel


router = APIRouter(
    prefix="/profile",
    tags=["destiny", "profile"],
)


@router.get("/discord/{discord_id}", response_model=DestinyProfileModel)
async def discord_get(discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return a users profile"""

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    return DestinyProfileModel.from_orm(profile)


@router.get("/destiny/{destiny_id}", response_model=DestinyProfileModel)
async def destiny_get(destiny_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return a users profile"""

    profile = await crud.discord_users.get_profile_from_destiny_id(db, destiny_id)
    return DestinyProfileModel.from_orm(profile)


@router.delete("/delete/{discord_id}", response_model=EmptyResponseModel)
async def discord_delete(discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Delete a users profile"""

    await crud.discord_users.delete_profile(db, discord_id)
    return EmptyResponseModel()


@router.get("/joinId/{discord_id}/get", response_model=DestinyProfileModel)
async def join_id_get(discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return a users join id"""

    join_id = await crud.discord_users.get_join_id(db=db, discord_id=discord_id)
    return DestinyJoinIdModel(join_id=join_id)


@router.post("/joinId/{discord_id}/update", response_model=DestinyProfileModel)
async def join_id_update(discord_id: int, data: DestinyJoinIdModel, db: AsyncSession = Depends(get_db_session)):
    """Update a users join id"""

    join_id = await crud.discord_users.update_join_id(db=db, discord_id=discord_id, new_join_id=data.join_id)
    return DestinyJoinIdModel(join_id=join_id)


@router.delete("/joinId/{discord_id}/delete", response_model=DestinyProfileModel)
async def join_id_get(discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Delete a users join id"""

    await crud.discord_users.delete_join_id(db=db, discord_id=discord_id)
    return EmptyResponseModel()
