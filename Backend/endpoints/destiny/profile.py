from fastapi import APIRouter

from Backend.crud import discord_users
from Backend.database import acquire_db_session
from Shared.networkingSchemas import EmptyResponseModel
from Shared.networkingSchemas.destiny.profile import DestinyHasTokenModel, DestinyProfileModel

router = APIRouter(
    prefix="/destiny/profile",
    tags=["destiny", "profile"],
)


@router.get("/discord/{discord_id}", response_model=DestinyProfileModel)  # has test
async def discord_get(discord_id: int):
    """Return a users profile"""

    async with acquire_db_session() as db:
        profile = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        return DestinyProfileModel.from_orm(profile)


@router.get("/{discord_id}/has_token", response_model=DestinyHasTokenModel)  # has test
async def discord_has_token(discord_id: int):
    """Return if a user has a valid token"""

    async with acquire_db_session() as db:
        profile = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        if not profile:
            return DestinyHasTokenModel(token=False, value=None)

    # get a working token
    await profile.auth.refresh()
    return DestinyHasTokenModel(token=True, value=profile.token)


@router.get("/{guild_id}/{discord_id}/registration_role/", response_model=EmptyResponseModel)  # has test
async def discord_registration_role(guild_id: int, discord_id: int):
    """Assign the registration role if applicable"""

    async with acquire_db_session() as db:
        await discord_users.add_registration_roles(db=db, discord_id=discord_id, guild_ids=[guild_id])

        return EmptyResponseModel()


@router.get("/destiny/{destiny_id}", response_model=DestinyProfileModel)  # has test
async def destiny_get(destiny_id: int):
    """Return a users profile"""

    async with acquire_db_session() as db:
        profile = await discord_users.get_profile_from_destiny_id(db, destiny_id)
        return DestinyProfileModel.from_orm(profile)


@router.delete("/{discord_id}/delete", response_model=EmptyResponseModel)  # has test
async def discord_delete(discord_id: int):
    """Delete a users profile"""

    async with acquire_db_session() as db:
        await discord_users.delete_profile(db, discord_id)
        return EmptyResponseModel()
