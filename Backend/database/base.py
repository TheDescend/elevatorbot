import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from settings import enable_debug_mode


DATABASE_URL = f"""postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOST")}:{os.environ.get("POSTGRES_PORT")}/{os.environ.get("POSTGRES_DB")}"""


engine = create_async_engine(
    DATABASE_URL,
    echo=enable_debug_mode
)
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
Base = declarative_base()
