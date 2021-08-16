from fastapi import Header, HTTPException

from Backend.database.base import async_session
from Backend.database.dataAccessLayers.book import BookDAL


async def get_token_header(x_token: str = Header(...)):
    if x_token != "possible-super-secret-header-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")

async def get_query_token(token: str):
    print('checking query token....')
    if token != "possible-super-secret-query-token":
        raise HTTPException(status_code=400, detail="No Jessica token provided")


async def get_book():
    async with async_session() as session:
        async with session.begin():
            yield BookDAL(session)