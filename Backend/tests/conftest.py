import asyncio

import pytest
import pytest_asyncio
from dummyData.insert import insert_dummy_data
from httpx import AsyncClient

# need to override the event loop to not close
from misc.test_bungio_events import TestingClient
from sqlalchemy import text

import Backend.bungio.client as bungie_client
from Backend.database.base import *
from Backend.database.models import create_tables
from Backend.main import app
from Backend.startup.initLogging import init_logging


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

    # create bungio client
    bungie_client._BUNGIO_CLIENT = TestingClient(
        bungie_client_id="bungie_client_id",
        bungie_client_secret="bungie_client_secret",
        bungie_token="bungie_token",
        manifest_storage=setup_engine(),
    )


# init the tables
@pytest_asyncio.fixture(scope="session")
async def init_db_tables(setup):
    # drop all tables
    async with setup_engine().begin() as connection:
        await connection.execute(text("DROP SCHEMA public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))
        await connection.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
        await connection.execute(text("GRANT ALL ON SCHEMA public TO public"))

    # create tables again
    await create_tables(engine=setup_engine())


# we also want the db object
@pytest_asyncio.fixture(scope="session", autouse=True)
async def db(init_db_tables) -> AsyncSession:
    # first, insert the dummy data
    async with acquire_db_session() as session:
        async with AsyncClient(app=app, base_url="http://testserver", follow_redirects=True) as client:
            await insert_dummy_data(db=session, client=client)

    # yield the session obj to the rest
    async with acquire_db_session() as session:
        yield session


# make it so that every function can get the client by just specifying it as a param
@pytest_asyncio.fixture(scope="session")
async def client(db) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://testserver", follow_redirects=True) as c:
        yield c
