from typing import Any, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

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


    async def _get_with_key(
        self,
        db: AsyncSession,
        primary_key: Any
    ) -> Optional[ModelType]:
        """ Returns the object by primary key or None """

        return await db.get(self.model, primary_key)


    async def _get_multi(
        self,
        db: AsyncSession,
        limit: int = 100,
    ) -> List[ModelType]:
        """ Returns a list of all the objects """

        query = select(self.model).limit(limit)
        result = await self._execute_query(db, query)
        return result.scalars().fetchall()


    async def _get_multi_with_filter(
        self,
        db: AsyncSession,
        limit: int = 100,
        **filter_kwargs,
    ) -> List[ModelType]:
        """ Returns a list of all the objects which fulfill the filter clauses """

        query = select(self.model).filter_by(**filter_kwargs).limit(limit)
        result = await self._execute_query(db, query)
        return result.scalars().fetchall()


    @staticmethod
    async def _insert(
        db: AsyncSession,
        to_create: ModelType
    ) -> None:
        """ Insert a initiated ModelType into the database """

        db.add(to_create)
        await db.flush()


    @staticmethod
    async def _update(
        db: AsyncSession,
        to_update: ModelType,
        **update_kwargs
    ) -> None:
        """ Update a initiated ModelType in the database """

        for key, value in update_kwargs.items():
            setattr(to_update, key, value)

        await db.flush()


    async def _delete(
        self,
        db: AsyncSession,
        primary_key: Any
    ) -> Optional[ModelType]:
        """ Delete an entry from the database by primary key """

        obj = await self._get_with_key(db, primary_key)

        # test if that actually exists
        if not obj:
            return None

        # _delete and return
        await db.delete(obj)
        await db.flush()

        return obj


    @staticmethod
    async def _execute_query(
        db: AsyncSession,
        query: Select
    ) -> Result:
        """ Returns the result from the query """

        result = await db.execute(
            query
        )
        await db.flush()

        return result
