from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.weapons import DestinyWeapons
from Backend.dependencies import get_db_session
from Backend.schemas.destiny.weapons import DestinyWeaponsModel

router = APIRouter(
    prefix="/destiny",
    tags=["destiny", "weapons"],
)


@router.get("/weapons", response_model=DestinyWeaponsModel)
async def get_all(db: AsyncSession = Depends(get_db_session)):
    """Return all weapons there currently are"""

    weapons = DestinyWeapons(db=db, user=None)
    return await weapons.get_all_weapons()


@router.get("/{guild_id}/{discord_id}/weapons/top", response_model=aaaaaaaaaaaa)
async def get_top(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get the users top weapons"""

    ...


@router.get("/{guild_id}/{discord_id}/weapons/weapon", response_model=aaaaaaaaaaaa)
async def get_weapon(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get the users stats for the specified weapon"""

    ...
