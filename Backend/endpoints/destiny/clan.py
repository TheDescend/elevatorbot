from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend import crud
from Backend.core.destiny.clan import DestinyClan
from Backend.dependencies import get_db_session
from Backend.schemas.destiny.clan import DestinyClanMembersModel, DestinyClanModel


router = APIRouter(
    prefix="/destiny/{guild_id}/{discord_id}/clan",
    tags=["destiny", "clan"],
)


@router.get("/get", response_model=DestinyClanModel)
async def get_clan(
    guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)
):
    """Return the clan id and name"""

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    clan = DestinyClan(db=db, user=profile)

    # get name and id
    clan_id, clan_name = await clan.get_clan_id_and_name()

    return DestinyClanModel(clan_id, clan_name)


@router.get("/get/members", response_model=DestinyClanMembersModel)
async def get_clan_members(
    guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)
):
    """Return the clan members"""

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    clan = DestinyClan(db=db, user=profile)

    members = await clan.get_clan_members()

    return DestinyClanMembersModel(members)


@router.get(
    "/get/members/search/{search_phrase}", response_model=DestinyClanMembersModel
)
async def get_clan_members_search(
    guild_id: int,
    discord_id: int,
    search_phrase: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Return the clan members which fulfill the search phrase"""

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    clan = DestinyClan(db=db, user=profile)

    members = await clan.search_clan_for_member(member_name=search_phrase)

    return DestinyClanMembersModel(members)


@router.get("/invite/{to_invite_discord_id}", response_model=None)
async def destiny_name(
    guild_id: int,
    discord_id: int,
    to_invite_discord_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Invite to_invite_discord_id to the clan"""

    # todo get the account which has admin perms for the ingame clan
    pass
