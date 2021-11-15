from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.profile import DestinyProfile
from Backend.crud import discord_users
from Backend.crud.destiny.items import destiny_items
from Backend.dependencies import get_db_session
from NetworkingSchemas.basic import NameModel, ValueModel

router = APIRouter(
    prefix="/destiny/items",
    tags=["destiny", "items"],
)


@router.get("/collectible/{collectible_id}", response_model=NameModel)
async def get_collectible_name(collectible_id: int, db: AsyncSession = Depends(get_db_session)):
    """Gets the collectible name"""

    result = await destiny_items.get_collectible(db=db, collectible_id=collectible_id)
    return NameModel(name=result.name) if result else NameModel(name=None)


@router.get("/triumph/{triumph_id}", response_model=NameModel)
async def get_triumph_name(triumph_id: int, db: AsyncSession = Depends(get_db_session)):
    """Gets the triumph name"""

    result = await destiny_items.get_record(db=db, triumph_id=triumph_id)
    return NameModel(name=result.name) if result else NameModel(name=None)
