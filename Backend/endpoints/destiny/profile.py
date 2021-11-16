from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend import crud
from Backend.crud import discord_users
from Backend.dependencies import get_db_session
from NetworkingSchemas.basic import EmptyResponseModel
from NetworkingSchemas.destiny.profile import DestinyHasTokenModel, DestinyProfileModel

router = APIRouter(
    prefix="/profile",
    tags=["destiny", "profile"],
)


@router.get("/discord/{discord_id}", response_model=DestinyProfileModel)
async def discord_get(discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return a users profile"""

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    return DestinyProfileModel.from_orm(profile)


@router.get("/discord/{discord_id}/has_token", response_model=DestinyHasTokenModel)
async def discord_has_token(discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return if a user has a valid token"""

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    no_token = await discord_users.token_is_expired(db=db, user=profile)

    return DestinyHasTokenModel(token=not no_token, value=profile.token if not no_token else None)


@router.get("/discord/{discord_id}/guild/{guild_id}/registration_role", response_model=EmptyResponseModel)
async def discord_registration_role(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Assign the registration role if applicable"""

    await discord_users.add_registration_roles(db=db, discord_id=discord_id, guild_ids=[guild_id])

    return EmptyResponseModel()


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
