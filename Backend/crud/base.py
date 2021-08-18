from typing import Any, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.database.base import Base



ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase:
    def __init__(self, model: Type[ModelType]):
        """
        A base CRUD object with default methods to Create, Read, Update, Delete

        **Parameters**
        * `model`: A SQLAlchemy model class
        """
        self.model = model


    async def get_with_key(
        self,
        db: AsyncSession,
        primary_key: Any
    ) -> Optional[ModelType]:
        """ Returns the object by primary key or None """

        return await db.get(self.model, primary_key)


    async def get_multi(
        self,
        db: AsyncSession,
        limit: int = 100,
    ) -> List[ModelType]:
        """ Returns a list of all the objects """

        results: Result = await db.execute(
            select(self.model).limit(limit)
        )
        return results.all()


    async def get_multi_with_column(
        self,
        db: AsyncSession,
        column_name: str,
        column_value: Any,
        limit: int = 100,
    ) -> List[ModelType]:
        """ Returns a list of all the objects which fulfill the where clause """

        results: Result = await db.execute(
            select(self.model).where(column_name == column_value).limit(limit)
        )
        return results.all()


    @staticmethod
    async def insert(
        db: AsyncSession,
        to_create: ModelType
    ) -> None:
        """ Insert a initiated ModelType into the database """

        db.add(to_create)
        await db.flush()


    @staticmethod
    async def update(
        db: AsyncSession,
        updated_db_obj: ModelType,
    ) -> None:
        """ Updates an entry with the **to_update kwargs """

        db.add(updated_db_obj)
        await db.flush()


    async def remove(
        self,
        db: AsyncSession,
        primary_key: Any
    ) -> Optional[ModelType]:
        """ Delete an entry from the database by primary key """

        obj = await self.get_with_key(db, primary_key)

        # test if that actually exists
        if not obj:
            return None

        # delete and return
        await db.delete(obj)
        await db.flush()

        return obj
