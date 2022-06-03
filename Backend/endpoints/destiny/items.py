from fastapi import APIRouter

from Backend.crud import destiny_manifest
from Backend.crud.destiny.items import destiny_items
from Backend.database import acquire_db_session
from Shared.networkingSchemas import DestinyAllCollectibleModel, DestinyAllTriumphModel, NameModel
from Shared.networkingSchemas.destiny import DestinyAllLoreModel

router = APIRouter(
    prefix="/destiny/items",
    tags=["destiny", "items"],
)


@router.get("/collectible/{collectible_id}", response_model=NameModel)  # has test
async def get_collectible_name(collectible_id: int):
    """Gets the collectible name"""

    async with acquire_db_session() as db:
        result = await destiny_items.get_collectible(db=db, collectible_id=collectible_id)
        return NameModel(name=result.name) if result else NameModel(name=None)


@router.get("/collectible/get/all", response_model=DestinyAllCollectibleModel)  # has test
async def collectible_get_all():
    """Return all collectibles and their hashes"""

    async with acquire_db_session() as db:
        return DestinyAllCollectibleModel(collectibles=await destiny_manifest.get_all_collectibles(db=db))


@router.get("/triumph/{triumph_id}", response_model=NameModel)  # has test
async def get_triumph_name(triumph_id: int):
    """Gets the triumph name"""

    async with acquire_db_session() as db:
        result = await destiny_items.get_record(db=db, record_id=triumph_id)
        return NameModel(name=result.name) if result else NameModel(name=None)


@router.get("/triumph/get/all", response_model=DestinyAllTriumphModel)  # has test
async def triumph_get_all():
    """Return all triumphs and their hashes"""

    async with acquire_db_session() as db:
        return DestinyAllTriumphModel(triumphs=await destiny_manifest.get_all_triumphs(db=db))


@router.get("/lore/get/all", response_model=DestinyAllLoreModel)  # has test
async def get_all_lore():
    """Return all lore"""

    async with acquire_db_session() as db:
        return DestinyAllLoreModel(items=await destiny_manifest.get_all_lore(db=db))
