from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend import crud
from Backend.core.destiny.profile import DestinyProfile
from Backend.dependencies import get_db_session
from Backend.schemas.destiny.account import (
    DestinyCharactersModel,
    DestinyNameModel,
    DestinyStatModel,
)
from Backend.schemas.destiny.profile import DestinyLowMansModel

router = APIRouter(
    prefix="/destiny/{guild_id}/{discord_id}/account",
    tags=["destiny", "account"],
)


@router.get("/name", response_model=DestinyNameModel)
async def destiny_name(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the destiny name"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    return DestinyNameModel(name=user.bungie_name)


@router.get("/solos", response_model=DestinyLowMansModel)
async def destiny_solos(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the destiny solos"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    # _get the solo data
    return await profile.get_solos()


@router.get("/characters", response_model=DestinyCharactersModel)
async def characters(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the characters with info on them"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    # _get the characters
    return await profile.get_character_info()


@router.get("/stat/{stat_category}/{stat_name}", response_model=DestinyStatModel)
async def stat(
    guild_id: int, discord_id: int, stat_category: str, stat_name: str, db: AsyncSession = Depends(get_db_session)
):
    """Return the stat value"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    # _get the stat value
    value = await profile.get_stat_value(stat_name=stat_name, stat_category=stat_category)

    return DestinyStatModel(value=value)


@router.get("/stat/characters/{stat_category}/{stat_name}", response_model=dict[int, DestinyStatModel])
async def stat_characters(
    guild_id: int, discord_id: int, stat_category: str, stat_name: str, db: AsyncSession = Depends(get_db_session)
):
    """Return the stat value by character_id"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    # _get character ids
    character_ids = await profile.get_character_ids()

    result = {}
    # loop through characters
    for character_id in character_ids:
        # _get the stat value
        value = await profile.get_stat_value(stat_name=stat_name, stat_category=stat_category)
        result.update({character_id: DestinyStatModel(value=value)})

    return result
