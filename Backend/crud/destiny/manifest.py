import dataclasses
from typing import Any, Optional, TypeVar

from sqlalchemy import not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import versions
from Backend.crud.base import CRUDBase
from Backend.database.base import Base
from Backend.database.models import (
    DestinyActivityDefinition,
    DestinyRecordDefinition,
    DestinySeasonPassDefinition,
)
from NetworkingSchemas.destiny import DestinyActivityModel

ModelType = TypeVar("ModelType", bound=Base)


@dataclasses.dataclass
class Seal:
    reference_id: int
    title_name: str


class CRUDManifest(CRUDBase):
    @staticmethod
    async def get_version(db: AsyncSession):
        """Get the current version"""

        return await versions.get(db=db, name="Manifest")

    @staticmethod
    async def upsert_version(db: AsyncSession, version: str):
        """Upsert the current version"""

        return await versions.upsert(db=db, name="Manifest", version=version)

    @staticmethod
    async def get(db: AsyncSession, table: ModelType, primary_key: Any) -> Optional[ModelType]:
        """Get data from specified table"""

        return await db.get(table, primary_key)

    async def delete_definition(self, db: AsyncSession, db_model: ModelType):
        """Delete all entries from the specified table"""

        # set table to the correct one
        self.model = db_model

        # delete table
        await self._delete_all(db=db)

    async def insert_definition(self, db: AsyncSession, db_model: ModelType, to_insert: list[ModelType]):
        """Insert the data into the table"""

        # set table to the correct one
        self.model = db_model

        # bulk insert
        await self._insert_multi(db=db, to_create=to_insert)

    async def get_seals(self, db: AsyncSession) -> list[Seal]:
        """Get all current seals"""

        # reference ids which should not get returned here
        not_available = []

        query = (
            select(DestinyRecordDefinition)
            .filter(DestinyRecordDefinition.has_title)
            .filter(not_(DestinyRecordDefinition.reference_id.in_(not_available)))
        )

        result = await self._execute_query(db=db, query=query)
        return [Seal(**row) for row in result.scalars().fetchall()]

    async def get_all_definitions(self, db: AsyncSession) -> list[DestinyActivityModel]:
        """Gets all activities"""

        # get them all from the db
        query = select(DestinyActivityDefinition)

        db_activities: list[DestinyActivityDefinition] = (
            (await self._execute_query(db=db, query=query)).scalars().fetchall()
        )

        # loop through all activities and save them by name
        data = {}
        for activity in db_activities:
            if activity.name not in data:
                data.update({activity.name: []})
            data[activity.name].append(activity)

        # format them correctly
        result = []
        for activities in data.values():
            result.append(
                DestinyActivityModel(
                    name=activities[0].name,
                    description=activities[0].description,
                    activity_ids=[activity.reference_id for activity in activities],
                )
            )

        return result

    async def get_current_season_pass(self, db: AsyncSession) -> DestinySeasonPassDefinition:
        """Get the current season pass from the DB"""

        query = select(DestinySeasonPassDefinition).order_by(DestinySeasonPassDefinition.index.asc()).limit(1)

        result = await self._execute_query(db=db, query=query)
        return result.scalar()


destiny_manifest = CRUDManifest(Base)
