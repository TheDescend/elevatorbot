import os

from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from settings import ENABLE_DEBUG_MODE


DATABASE_URL = f"""postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOST")}:{os.environ.get("POSTGRES_PORT")}/{os.environ.get("POSTGRES_DB")}"""
_ENGINE = None
_SESSION = None
_TEST_MODE = True


Base = declarative_base()


def setup_engine(database_url: str = DATABASE_URL) -> Engine:
    global _ENGINE

    if not _ENGINE:
        _ENGINE = create_async_engine(
            database_url,
            future=True,
            echo=bool(ENABLE_DEBUG_MODE and not is_test_mode()),
        )

    return _ENGINE


def get_async_session() -> sessionmaker:
    global _SESSION

    if not _SESSION:
        _SESSION = sessionmaker(
            setup_engine(),
            class_=AsyncSession,
            future=True,
        )
    return _SESSION


def is_test_mode(set_test_mode: bool = None) -> bool:
    global _TEST_MODE

    if set_test_mode is not None:
        _TEST_MODE = set_test_mode

    return _TEST_MODE
