from fastapi import APIRouter

from Backend.crud import destiny_manifest
from Shared.networkingSchemas import (
    DestinyAllCollectibleModel,
    DestinyAllTriumphModel,
    DestinyNamedItemModel,
    NameModel,
)
from Shared.networkingSchemas.destiny import DestinyAllLoreModel

router = APIRouter(
    prefix="/destiny/items",
    tags=["destiny", "items"],
)


@router.get("/collectible/{collectible_id}", response_model=NameModel)  # has test
async def get_collectible_name(collectible_id: int):
    """Gets the collectible name"""

    results = await destiny_manifest.get_all_collectibles()
    result = results.get(collectible_id)
    return NameModel(name=result.display_properties.name) if result else NameModel(name=None)


@router.get("/collectible/get/all", response_model=DestinyAllCollectibleModel)  # has test
async def collectible_get_all():
    """Return all collectibles and their hashes"""

    results = await destiny_manifest.get_all_collectibles()

    pydantic_items: list[DestinyNamedItemModel] = [
        DestinyNamedItemModel(reference_id=item.hash, name=item.display_properties.name)
        for item in results
        if item.display_properties.name
    ]
    return DestinyAllCollectibleModel(collectibles=sorted(pydantic_items, key=lambda item: item.name))


@router.get("/triumph/{triumph_id}", response_model=NameModel)  # has test
async def get_triumph_name(triumph_id: int):
    """Gets the triumph name"""

    results = await destiny_manifest.get_all_triumphs()
    result = results.get(triumph_id)
    return NameModel(name=result.display_properties.name) if result else NameModel(name=None)


@router.get("/triumph/get/all", response_model=DestinyAllTriumphModel)  # has test
async def triumph_get_all():
    """Return all triumphs and their hashes"""

    results = await destiny_manifest.get_all_triumphs()

    pydantic_items: list[DestinyNamedItemModel] = [
        DestinyNamedItemModel(reference_id=item.hash, name=item.display_properties.name)
        for item in results
        if item.display_properties.name
    ]
    return DestinyAllCollectibleModel(collectibles=sorted(pydantic_items, key=lambda item: item.name))


@router.get("/lore/get/all", response_model=DestinyAllLoreModel)  # has test
async def get_all_lore():
    """Return all lore"""

    res = await destiny_manifest.get_all_lore()
    return DestinyAllLoreModel(collectibles=list(res.values()))
