import os

from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from settings import ENABLE_DEBUG_MODE


_ENGINE = None
_SESSION = None


Base = declarative_base()


def setup_engine() -> Engine:
    global _ENGINE

    if not _ENGINE:
        DATABASE_URL = f"""postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOST")}:{os.environ.get("POSTGRES_PORT")}/{os.environ.get("POSTGRES_DB")}"""

        _ENGINE = create_async_engine(
            DATABASE_URL,
            future=True,
            echo=ENABLE_DEBUG_MODE,
        )

    return _ENGINE


def get_async_session() -> sessionmaker:
    global _SESSION

    if not _SESSION:
        _SESSION = sessionmaker(
            setup_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _SESSION
