from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend import crud
from Backend.core.destiny.clan import DestinyClan
from Backend.core.errors import CustomException
from Backend.dependencies import get_db_session
from Backend.schemas.destiny.clan import DestinyClanLink, DestinyClanMembersModel, DestinyClanModel


router = APIRouter(
    prefix="/destiny/{guild_id}/{discord_id}/clan",
    tags=["destiny", "clan"],
)


@router.get("/get", response_model=DestinyClanModel)
async def get_clan(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the clan id and name"""

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    clan = DestinyClan(db=db, user=profile)

    # get name and id
    clan_id, clan_name = await clan.get_clan_id_and_name()

    return DestinyClanModel(clan_id=clan_id, clan_name=clan_name)


@router.get("/get/members", response_model=DestinyClanMembersModel)
async def get_clan_members(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the clan members"""

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    clan = DestinyClan(db=db, user=profile)

    members = await clan.get_clan_members()

    return DestinyClanMembersModel(members=members)


@router.post("/link/", response_model=DestinyClanLink)
async def link_clan(
    guild_id: int,
    discord_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Links the discord guild to the destiny clan"""

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    clan = DestinyClan(db=db, user=profile)

    clan_id, clan_name = await clan.get_clan_id_and_name()

    # check if discord user is admin
    if not await clan.is_clan_admin(clan_id):
        raise CustomException("ClanNoPermissions")

    await crud.destiny_clan_links.link(db=db, discord_id=discord_id, discord_guild_id=guild_id, destiny_clan_id=clan_id)

    return DestinyClanLink(success=True, clan_name=clan_name)


@router.post("/unlink/", response_model=DestinyClanLink)
async def unlink_clan(
    guild_id: int,
    discord_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Unlinks the discord guild from the destiny clan"""

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    clan = DestinyClan(db=db, user=profile)

    clan_id, clan_name = await clan.get_clan_id_and_name()

    await crud.destiny_clan_links.unlink(
        db=db,
        discord_guild_id=guild_id,
    )

    return DestinyClanLink(success=True, clan_name=clan_name)


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
