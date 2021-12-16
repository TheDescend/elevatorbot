import asyncio
import os
import sys

import pytest
from dummyData.insert import insert_dummy_data
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.database.base import get_async_session, is_test_mode, setup_engine
from Backend.database.models import create_tables
from Backend.main import app

# enable test mode
is_test_mode(set_test_mode=True)

# insert a local testing db
TESTING_DATABASE_URL = f"""postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@localhost:{os.environ.get("POSTGRES_PORT")}/postgres"""
setup_engine(database_url=TESTING_DATABASE_URL)

#  need to override the event loop to not close
@pytest.fixture(scope="session", autouse=True)
def event_loop():
    if sys.platform.startswith("win") and sys.version_info[:2] >= (3, 8):
        # Avoid "RuntimeError: Event loop is closed" on Windows when tearing down tests
        # https://github.com/encode/httpx/issues/914
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# init the tables
@pytest.fixture(scope="session", autouse=True)
async def init_db_tables():
    await create_tables(engine=setup_engine())


# make it so that every function can get the client by just specifying it as a param
@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://testserver", follow_redirects=True) as client:
        yield client


# we also want the db object
@pytest.fixture(scope="session")
async def db() -> AsyncSession:
    async with get_async_session().begin() as session:
        yield session


# insert the dummy data into the tables
@pytest.fixture(scope="session", autouse=True)
async def populate_tables(db: AsyncSession):
    await insert_dummy_data(db=db)
