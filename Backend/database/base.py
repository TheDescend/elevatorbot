import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncContextManager, Optional, Self

import orjson
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from Shared.functions.readSettingsFile import get_setting

POSTGRES_USER = os.environ.get("POSTGRES_USER")
assert POSTGRES_USER
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
assert POSTGRES_PASSWORD
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
assert POSTGRES_HOST
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
assert POSTGRES_PORT
POSTGRES_DB = os.environ.get("POSTGRES_DB")
assert POSTGRES_DB


DATABASE_URL = (
    f"""postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"""
)
_ENGINE = None
_SESSIONMAKER = None
_TEST_MODE = False


_Base = declarative_base()


class Base(_Base):
    def update_from_class(self, other_class: Self):
        if id(self) != id(other_class):
            for key, value in other_class.__dict__.items():
                if not key.startswith("_"):
                    setattr(self, key, value)


def setup_engine(database_url: str = DATABASE_URL) -> Engine:
    global _ENGINE

    if not _ENGINE:
        _ENGINE = create_async_engine(
            database_url,
            future=True,
            echo=bool(get_setting("ENABLE_DEBUG_MODE") and not is_test_mode()),
            echo_pool=bool(get_setting("ENABLE_DEBUG_MODE") and not is_test_mode()),
            json_deserializer=orjson.loads,
            json_serializer=lambda x: orjson.dumps(x).decode(),
            pool_pre_ping=True,
            pool_size=50,
            max_overflow=125,
            pool_timeout=300,
        )

    return _ENGINE


def get_async_sessionmaker() -> sessionmaker:
    global _SESSIONMAKER

    # if expire_on_commit is enabled, our own cache would get expired after every session close
    # since we are careful and update the cache when we change an object, that should not be a problem
    if not _SESSIONMAKER:
        _SESSIONMAKER = sessionmaker(bind=setup_engine(), class_=AsyncSession, future=True, expire_on_commit=False)
    return _SESSIONMAKER


def is_test_mode(set_test_mode: Optional[bool] = None) -> bool:
    global _TEST_MODE

    if set_test_mode is not None:
        _TEST_MODE = set_test_mode

    return _TEST_MODE


@asynccontextmanager
async def acquire_db_session() -> AsyncContextManager[AsyncSession]:
    """Get a database session"""

    db = get_async_sessionmaker()()
    logger = logging.getLogger("db")

    if not db.in_transaction():
        async with db.begin():
            yield db
    else:
        logger.debug("Already in transaction")
        yield db
        if db.in_transaction():
            await db.commit()
            logger.debug("Implicit transaction commit")
