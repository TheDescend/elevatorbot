from fastapi import APIRouter, Depends, HTTPException

from Backend.database.dataAccessLayers.book import BookDAL
from Backend.dependencies.databaseObjects import get_book

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)


fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get("/")
async def read_items():
    return fake_items_db


@router.get("/{item_id}")
async def read_item(item_id: str, book_dal: BookDAL = Depends(get_book)):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    # do some db stuff
    await book_dal.create_book("Very good book", "kigstn", 2022)

    return {"name": fake_items_db[item_id]["name"], "item_id": item_id}


@router.put(
    "/{item_id}",
    tags=["custom"],
    responses={403: {"description": "Operation forbidden"}},
)
async def update_item(item_id: str):
    if item_id != "plumbus":
        raise HTTPException(
            status_code=403, detail="You can only update the item: plumbus"
        )
    return {"item_id": item_id, "name": "The great Plumbus"}