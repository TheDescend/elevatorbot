import dataclasses
from typing import Any, Optional, TypeVar

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import versions
from Backend.crud.base import CRUDBase
from Backend.database.base import Base
from Backend.database.models import (
    DestinyActivityDefinition,
    DestinyLoreDefinition,
    DestinySeasonPassDefinition,
    Versions,
)
from Backend.misc.cache import cache
from DestinyEnums.enums import UsableDestinyActivityModeTypeEnum
from NetworkingSchemas.destiny.activities import DestinyActivityModel
from NetworkingSchemas.destiny.items import DestinyLoreModel

ModelType = TypeVar("ModelType", bound=Base)


@dataclasses.dataclass
class Seal:
    reference_id: int
    title_name: str


class CRUDManifest(CRUDBase):
    @staticmethod
    async def get_version(db: AsyncSession) -> Optional[Versions]:
        """Get the current version"""

        return await versions.get(db=db, name="Manifest")

    @staticmethod
    async def upsert_version(db: AsyncSession, version: str) -> Versions:
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

    async def get_all_activities(self, db: AsyncSession) -> list[DestinyActivityModel]:
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
                    mode=activities[0].direct_activity_mode_type,
                )
            )

        return result

    async def get_all_lore(self, db: AsyncSession) -> list[DestinyLoreModel]:
        """Gets all lore"""

        # get them all from the db
        query = select(DestinyLoreDefinition)

        db_lore: list[DestinyLoreDefinition] = (await self._execute_query(db=db, query=query)).scalars().fetchall()

        # format them correctly
        return [DestinyLoreModel.from_orm(lore) for lore in db_lore]

    async def get_grandmaster_nfs(self, db: AsyncSession) -> list[DestinyActivityModel]:
        """Get all grandmaster nfs"""

        query = select(DestinyActivityDefinition)
        query = query.filter(
            DestinyActivityDefinition.activity_mode_types.any(UsableDestinyActivityModeTypeEnum.NIGHTFALL.value)
        )
        query = query.filter(
            or_(DestinyActivityDefinition.name.like(f"%Grandmaster%")),
            (DestinyActivityDefinition.activity_light_level == 1100),
        )

        results = await self._execute_query(db=db, query=query)
        db_result: list[DestinyActivityDefinition] = results.scalars().all()

        # loop through all activities and save them by name
        data = {}
        for activity in db_result:
            if activity.description not in data:
                data.update({activity.description: []})
            data[activity.description].append(activity)

        # contains all gm ids
        all_grandmaster = DestinyActivityModel(
            name="Grandmaster: All",
            description="Grandmaster: All",
            activity_ids=[],
        )

        # format them correctly
        result = []
        for activities in data.values():
            all_grandmaster.activity_ids.append(activities[0].reference_id)
            result.append(
                DestinyActivityModel(
                    name=f"Grandmaster: {activities[0].description}",
                    description=f"Grandmaster: {activities[0].description}",
                    activity_ids=[activity.reference_id for activity in activities],
                    mode=activities[0].direct_activity_mode_type,
                )
            )

        result.insert(0, all_grandmaster)
        return result

    async def get_challenging_solo_activities(self, db: AsyncSession) -> list[DestinyActivityModel]:
        """Get activities that are difficult to solo"""

        # check cache
        if not cache.interesting_solos:
            # todo pirate dungeon name
            interesting_solos = [
                "Shattered Throne",
                "Pit of Heresy",
                "Prophecy",
                "Harbinger",
                "Presage",
                "Master Presage",
                "The Whisper",
                "Zero Hour",
                "Grandmaster Nightfalls",
            ]

            # loop through each of the entries
            for activity_name in interesting_solos:
                query = select(DestinyActivityDefinition)
                query = query.filter(DestinyActivityDefinition.name.like(f"%{activity_name}%"))

                db_results = await self._execute_query(db=db, query=query)
                db_result: list[DestinyActivityDefinition] = db_results.scalars().all()

                # loop through all activities and save them by name
                data = None
                for activity in db_result:
                    if not data:
                        data = DestinyActivityModel(
                            name=activity.name,
                            description=activity.description,
                            activity_ids=[activity.reference_id],
                            mode=activity.direct_activity_mode_type,
                        )
                    else:
                        data.activity_ids.append(activity.reference_id)

                # check that we got some
                assert data

                cache.interesting_solos.append(data)

        return cache.interesting_solos

    async def get_current_season_pass(self, db: AsyncSession) -> DestinySeasonPassDefinition:
        """Get the current season pass from the DB"""

        query = select(DestinySeasonPassDefinition).order_by(DestinySeasonPassDefinition.index.asc()).limit(1)

        result = await self._execute_query(db=db, query=query)
        return result.scalar()


destiny_manifest = CRUDManifest(Base)
