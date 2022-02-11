from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud import discord_users
from Backend.dependencies import get_db_session
from Backend.networking.bungieAuth import BungieAuth
from Shared.networkingSchemas import EmptyResponseModel
from Shared.networkingSchemas.destiny.profile import DestinyHasTokenModel, DestinyProfileModel

router = APIRouter(
    prefix="/destiny/profile",
    tags=["destiny", "profile"],
)


@router.get("/discord/{discord_id}", response_model=DestinyProfileModel)  # has test
async def discord_get(discord_id: int):
    """Return a users profile"""

    profile = await discord_users.get_profile_from_discord_id(discord_id)
    return DestinyProfileModel.from_orm(profile)


@router.get("/{discord_id}/has_token", response_model=DestinyHasTokenModel)  # has test
async def discord_has_token(discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return if a user has a valid token"""

    no_token = DestinyHasTokenModel(token=False, value=None)

    profile = await discord_users.get_profile_from_discord_id(discord_id)
    if not profile:
        return no_token

    # get a working token
    auth = BungieAuth(db=db, user=profile)
    try:
        await auth.get_working_token()
    except CustomException as error:
        if error.error == "NoToken":
            return no_token
        raise error

    else:
        return DestinyHasTokenModel(token=not no_token, value=profile.token if not no_token else None)


@router.get("/{guild_id}/{discord_id}/registration_role/", response_model=EmptyResponseModel)  # has test
async def discord_registration_role(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Assign the registration role if applicable"""

    await discord_users.add_registration_roles(db=db, discord_id=discord_id, guild_ids=[guild_id])

    return EmptyResponseModel()


@router.get("/destiny/{destiny_id}", response_model=DestinyProfileModel)  # has test
async def destiny_get(destiny_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return a users profile"""

    profile = await discord_users.get_profile_from_destiny_id(db, destiny_id)
    return DestinyProfileModel.from_orm(profile)


@router.delete("/{discord_id}/delete", response_model=EmptyResponseModel)  # has test
async def discord_delete(discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Delete a users profile"""

    await discord_users.delete_profile(db, discord_id)
    return EmptyResponseModel()
