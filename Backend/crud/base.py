import asyncio
from typing import Any, List, Optional, Type, TypeVar

from sqlalchemy import delete, inspect, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.sql import Select

from Backend.database.base import Base, get_async_session

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase:
    def __init__(self, model: Type[ModelType]):
        """
        A base CRUD object with default methods to Create, Read, Update, Delete

        **Parameters**
        * `model`: A SQLAlchemy model class
        """
        self.model = model

    async def _get_with_key(self, db: AsyncSession, primary_key: Any) -> Optional[ModelType]:
        """Returns the object by primary key or None"""

        return await db.get(self.model, primary_key)

    async def _get_all(self, db: AsyncSession) -> List[ModelType]:
        """Returns a list of all the objects"""

        return await self._get_multi(db=db)

    async def _get_multi(self, db: AsyncSession, limit: Optional[int] = None, **filter_kwargs) -> List[ModelType]:
        """Returns a list of all the objects which fulfill the filter clauses"""

        query = select(self.model)

        if filter_kwargs:
            query = query.filter_by(**filter_kwargs)

        if limit:
            query = query.limit(limit)

        result = await self._execute_query(db, query)
        return result.scalars().fetchall()

    @staticmethod
    async def _insert(db: AsyncSession, to_create: ModelType) -> None:
        """Insert a initiated ModelType into the database"""

        db.add(to_create)
        await db.flush()

    @staticmethod
    async def _insert_multi(db: AsyncSession, to_create: list[ModelType]) -> None:
        """Insert initiated ModelTypes into the database"""

        db.add_all(to_create)
        await db.flush()

    async def _upsert(self, db: AsyncSession, model_data: dict) -> ModelType:
        """Upsert the item. Doesn't work with foreign keys"""

        async with asyncio.Lock():
            # prepare insert
            stmt = postgresql.insert(self.model).values(model_data)

            # get primary key and info what should be updated if it fails
            primary_keys = [key.name for key in inspect(self.model).primary_key]
            update_dict = {c.name: c for c in stmt.excluded if not c.primary_key}
            if not update_dict:
                raise ValueError(
                    f"_upsert() resulted in an empty update_dict for model '{self.model}', model_data: '{model_data}'"
                )

            # add upsert clause
            stmt = stmt.on_conflict_do_update(index_elements=primary_keys, set_=update_dict).returning(self.model)

            # convert that to orm
            query = select(self.model).from_statement(stmt).execution_options(populate_existing=True)

            result = await self._execute_query(db=db, query=query)
            return result.scalars().one()

    @staticmethod
    async def _mass_insert(db: AsyncSession, to_create: list[ModelType]) -> None:
        """Insert a initiated ModelType into the database"""

        db.add_all(to_create)
        await db.flush()

    @staticmethod
    async def _update(db: AsyncSession, to_update: ModelType, **update_kwargs) -> ModelType:
        """Update a initiated ModelType in the database"""

        for key, value in update_kwargs.items():
            setattr(to_update, key, value)

            # make sure to set them as modified
            # otherwise they might not get updated
            flag_modified(to_update, key)

        # test if the obj is detached, then we need to renew it briefly
        state = inspect(to_update)
        if state.detached:
            async with get_async_session().begin() as new_db:
                # merge the obj, since updating does not work with detached objs
                new_obj = await new_db.merge(to_update)
            return new_obj

        # only flush if it was not detached
        else:
            await db.flush()
            return to_update

    async def _delete(
        self, db: AsyncSession, primary_key: Optional[Any] = None, obj: Optional[ModelType] = None
    ) -> Optional[ModelType]:
        """Delete an entry from the database by primary key"""

        assert primary_key or obj

        if not obj:
            obj = await self._get_with_key(db, primary_key)

        # test if that actually exists
        if not obj:
            return None

        # delete and return
        await db.delete(obj)
        await db.flush()

        return obj

    async def _delete_multi(self, db: AsyncSession, **delete_kwargs) -> list[ModelType]:
        """Delete all entries from the table"""

        # get the objects
        objs = await self._get_multi(db=db, **delete_kwargs)

        # delete and return
        for obj in objs:
            await db.delete(obj)
        await db.flush()

        return objs

    async def _delete_all(self, db: AsyncSession):
        """Delete all entries from the table"""

        query = delete(self.model)

        await self._execute_query(db=db, query=query)

    @staticmethod
    async def _execute_query(db: AsyncSession, query: Select) -> Result:
        """Returns the result from the query"""

        result = await db.execute(query)
        await db.flush()

        return result
