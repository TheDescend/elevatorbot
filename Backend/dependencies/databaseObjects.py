from Backend.database.base import async_session
from Backend.database.dataAccessLayers.backendUser import BackendUserDAL
from Backend.database.dataAccessLayers.book import BookDAL


async def get_backend_user():
    async with async_session() as session:
        async with session.begin():
            yield BackendUserDAL(session)


async def get_book():
    async with async_session() as session:
        async with session.begin():
            yield BookDAL(session)
