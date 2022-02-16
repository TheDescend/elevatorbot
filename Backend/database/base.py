import os
from typing import Optional

import orjson
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from Shared.functions.readSettingsFile import get_setting

DATABASE_URL = f"""postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOST")}:{os.environ.get("POSTGRES_PORT")}/{os.environ.get("POSTGRES_DB")}"""
_ENGINE = None
_SESSION = None
_TEST_MODE = False


Base = declarative_base()


def setup_engine(database_url: str = DATABASE_URL) -> Engine:
    global _ENGINE

    if not _ENGINE:
        _ENGINE = create_async_engine(
            database_url,
            future=True,
            echo=bool(get_setting("ENABLE_DEBUG_MODE") and not is_test_mode()),
            json_deserializer=orjson.loads,
            json_serializer=lambda x: orjson.dumps(x).decode(),
            pool_pre_ping=True,
            pool_size=50,
            max_overflow=200,
            pool_timeout=60,
        )

    return _ENGINE


def get_async_session() -> sessionmaker:
    global _SESSION

    # if expire_on_commit is enabled, our own cache would get expired after every session close
    # since we are careful and update the cache when we change an object, that should not be a problem
    if not _SESSION:
        _SESSION = sessionmaker(bind=setup_engine(), class_=AsyncSession, future=True, expire_on_commit=False)
    return _SESSION


def is_test_mode(set_test_mode: Optional[bool] = None) -> bool:
    global _TEST_MODE

    if set_test_mode is not None:
        _TEST_MODE = set_test_mode

    return _TEST_MODE
