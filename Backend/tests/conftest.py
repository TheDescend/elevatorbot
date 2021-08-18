import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from Backend.database.base import is_test_mode, setup_engine
from Backend.main import app


# enable test mode
is_test_mode(set_test_mode=True)


# create a local testing db
TESTING_DATABASE_URL = f"""postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@localhost:{os.environ.get("POSTGRES_PORT")}/postgres"""
setup_engine(database_url=TESTING_DATABASE_URL)


# make it so that every function can get the client by just specifying it as a param
@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as client:
        yield client
