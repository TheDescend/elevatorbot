from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import AsyncConnection

from Backend.database.base import Base


# all table models are in here, allowing for easy generation
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    author = Column(String, nullable=False)
    release_year = Column(Integer, nullable=False)


# create all tables
async def create_tables(connection: AsyncConnection):
    await connection.run_sync(Base.metadata.drop_all)
