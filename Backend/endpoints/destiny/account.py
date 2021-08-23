from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.profile import DestinyProfile
from Backend.dependencies import get_db_session
from Backend import crud
from Backend.schemas.destiny.account import DestinyNameModel


router = APIRouter(
    prefix="/destiny/{guild_id}/{discord_id}/account",
    tags=["destiny", "account"],
)


@router.get("/name", response_model=DestinyNameModel)
async def destiny_name(
    guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)
):
    """Return the destiny name"""

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    user = DestinyProfile(db=db, user=profile)

    # get name
    name = await user.get_destiny_name()

    return DestinyNameModel(name)
