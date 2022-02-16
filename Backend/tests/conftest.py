import asyncio
import os

import pytest
from dummyData.insert import insert_dummy_data
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.database.base import get_async_session, is_test_mode, setup_engine
from Backend.database.models import create_tables
from Backend.main import app
from Backend.misc.initLogging import init_logging


# need to override the event loop to not close
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# set up some important variables
@pytest.fixture(scope="session")
def setup(event_loop):
    # enable test mode
    is_test_mode(set_test_mode=True)

    # create the logs
    init_logging()

    # insert a local testing db
    TESTING_DATABASE_URL = f"""postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@localhost:{os.environ.get("POSTGRES_PORT")}/postgres"""
    setup_engine(database_url=TESTING_DATABASE_URL)


# init the tables
@pytest.fixture(scope="session")
async def init_db_tables(setup):
    await create_tables(engine=setup_engine())


# we also want the db object
@pytest.fixture(scope="session", autouse=True)
async def db(init_db_tables) -> AsyncSession:
    # first, insert the dummy data
    async with get_async_session().begin() as session:
        async with AsyncClient(app=app, base_url="http://testserver", follow_redirects=True) as client:
            await insert_dummy_data(db=session, client=client)

    # yield the session obj to the rest
    async with get_async_session().begin() as session:
        yield session


# make it so that every function can get the client by just specifying it as a param
@pytest.fixture(scope="session")
async def client(db) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://testserver", follow_redirects=True) as client:
        yield client
