from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.misc.giveaway import crud_giveaway
from Backend.dependencies import get_db_session
from Shared.networkingSchemas import EmptyResponseModel
from Shared.networkingSchemas.misc.giveaway import GiveawayModel

router = APIRouter(
    prefix="/giveaway/{guild_id}/{discord_id}/{giveaway_id}",
    tags=["giveaway"],
)


@router.get("/get", response_model=GiveawayModel)  # has test
async def get(guild_id: int, discord_id: int, giveaway_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get the giveaway"""

    result = await crud_giveaway.get(db=db, giveaway_id=giveaway_id)
    return GiveawayModel.from_orm(result)


@router.post("/create", response_model=EmptyResponseModel)  # has test
async def create(guild_id: int, discord_id: int, giveaway_id: int, db: AsyncSession = Depends(get_db_session)):
    """Create a giveaway"""

    await crud_giveaway.create(db=db, giveaway_id=giveaway_id, author_id=discord_id, guild_id=guild_id)
    return EmptyResponseModel()


@router.post("/insert", response_model=GiveawayModel)  # has test
async def insert(guild_id: int, discord_id: int, giveaway_id: int, db: AsyncSession = Depends(get_db_session)):
    """Insert the user into the giveaway"""

    result = await crud_giveaway.insert(db=db, giveaway_id=giveaway_id, discord_id=discord_id)
    return GiveawayModel.from_orm(result)


@router.post("/remove", response_model=GiveawayModel)  # has test
async def remove(guild_id: int, discord_id: int, giveaway_id: int, db: AsyncSession = Depends(get_db_session)):
    """Remove a user from the giveaway"""

    result = await crud_giveaway.remove(db=db, giveaway_id=giveaway_id, discord_id=discord_id)
    return GiveawayModel.from_orm(result)
