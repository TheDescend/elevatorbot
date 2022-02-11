import asyncio
import dataclasses
from typing import Any, Optional, TypeVar

from sqlalchemy import not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.crud.misc.versions import versions
from Backend.database.base import Base, is_test_mode
from Backend.database.models import (
    DestinyActivityDefinition,
    DestinyCollectibleDefinition,
    DestinyLoreDefinition,
    DestinyRecordDefinition,
    DestinySeasonPassDefinition,
    Versions,
)
from Backend.misc.cache import cache
from Shared.enums.destiny import UsableDestinyActivityModeTypeEnum
from Shared.networkingSchemas import DestinyNamedItemModel
from Shared.networkingSchemas.destiny import DestinyActivityModel, DestinyLoreModel

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
                    name=activities[0].name or "Unknown",
                    description=activities[0].description,
                    matchmade=activities[0].matchmade,
                    max_players=activities[0].max_players,
                    activity_ids=[activity.reference_id for activity in activities],
                    mode=activities[0].direct_activity_mode_type,
                    image_url=activities[0].pgcr_image_url,
                )
            )

        sorted_result = sorted(result, key=lambda entry: entry.name)

        return sorted_result

    async def get_all_collectibles(self, db: AsyncSession) -> list[DestinyNamedItemModel]:
        """Gets all collectibles"""

        return await self._get_all_named_items(db=db, table=DestinyCollectibleDefinition)

    async def get_all_triumphs(self, db: AsyncSession) -> list[DestinyNamedItemModel]:
        """Gets all triumphs"""

        return await self._get_all_named_items(db=db, table=DestinyRecordDefinition)

    async def _get_all_named_items(self, db: AsyncSession, table: ModelType) -> list[DestinyNamedItemModel]:
        """Gets all named items"""

        # get them all from the db
        query = select(table)
        db_items: list[table] = (await self._execute_query(db=db, query=query)).scalars().fetchall()

        pydantic_items = [DestinyNamedItemModel.from_orm(item) for item in db_items if item.name]

        return sorted(pydantic_items, key=lambda entry: entry.name)

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
            or_(
                DestinyActivityDefinition.name.contains("Grandmaster"),
                (DestinyActivityDefinition.activity_light_level == 1100),
            )
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
            matchmade=False,
            max_players=3,
            activity_ids=[],
        )

        # format them correctly
        result = []
        for activities in data.values():
            all_grandmaster.activity_ids.extend(activity.reference_id for activity in activities)
            result.append(
                DestinyActivityModel(
                    name=f"Grandmaster: {activities[0].description}",
                    description=f"Grandmaster: {activities[0].description}",
                    matchmade=activities[0].matchmade,
                    max_players=activities[0].max_players,
                    activity_ids=[activity.reference_id for activity in activities],
                    mode=activities[0].direct_activity_mode_type,
                    image_url=activities[0].pgcr_image_url,
                )
            )

        result.insert(0, all_grandmaster)
        return result

    async def get_challenging_solo_activities(self, db: AsyncSession) -> dict[str, list[DestinyActivityModel]]:
        """Get activities that are difficult to solo"""

        async with asyncio.Lock():
            # check cache
            if not cache.interesting_solos:
                # key is the topic, then the activity display name
                # the value is a list with list[0] being what string the activity name has to include list[1] and what to exclude
                interesting_solos = {
                    "Dungeons": {
                        "Shattered Throne": ["Shattered Throne", None],
                        "Pit of Heresy": ["Pit of Heresy", None],
                        "Prophecy": ["Prophecy", None],
                        "Grasp of Avarice: Normal": ["Grasp of Avarice: Legend", None],
                        "Grasp of Avarice: Master": ["Grasp of Avarice: Master", None],
                    },
                    "Raids": {
                        "Eater of Worlds": ["Eater of Worlds", None],
                        "Last Wish": ["Last Wish", None],
                        "Vault of Glass": ["Vault of Glass", None],
                    },
                    "Story Missions": {
                        "The Whisper: Normal": ["The Whisper", "Heroic"],
                        "The Whisper: Master": ["The Whisper (Heroic)", None],
                        "Zero Hour: Normal": ["Zero Hour", "Heroic"],
                        "Zero Hour: Master": ["Zero Hour (Heroic)", None],
                        "Harbinger": ["Harbinger", None],
                        "Presage: Normal": ["Presage: Normal", None],
                        "Presage: Master": ["Presage: Master", None],
                    },
                    "Miscellaneous": {"Grandmaster Nightfalls": "grandmaster_nf"},
                }

                # loop through each of the entries
                for category, items in interesting_solos.items():
                    if category not in cache.interesting_solos:
                        cache.interesting_solos[category] = []

                    for activity_name, search_data in items.items():
                        # special handling for grandmasters
                        if search_data == "grandmaster_nf":
                            gms = await self.get_grandmaster_nfs(db=db)

                            # all gms is the first index there
                            data = gms[0]
                            data.name = activity_name

                        else:
                            query = select(DestinyActivityDefinition)
                            query = query.filter(DestinyActivityDefinition.name.contains(search_data[0]))

                            # do we want to exclude a search string
                            if search_data[1]:
                                query = query.filter(not_(DestinyActivityDefinition.name.contains(search_data[1])))

                            db_results = await self._execute_query(db=db, query=query)
                            db_result: list[DestinyActivityDefinition] = db_results.scalars().all()

                            # loop through all activities and save them by name
                            data = None
                            for activity in db_result:
                                if not data:
                                    data = DestinyActivityModel(
                                        name=activity_name,
                                        description=activity.description,
                                        matchmade=activity.matchmade,
                                        max_players=activity.max_players,
                                        activity_ids=[activity.reference_id],
                                        mode=activity.direct_activity_mode_type,
                                        image_url=activity.pgcr_image_url,
                                    )
                                else:
                                    data.activity_ids.append(activity.reference_id)

                        # check that we got some
                        if not is_test_mode():
                            assert data is not None

                        if data:
                            cache.interesting_solos[category].append(data)

            return cache.interesting_solos

    async def get_current_season_pass(self, db: AsyncSession) -> DestinySeasonPassDefinition:
        """Get the current season pass from the DB"""

        query = select(DestinySeasonPassDefinition).order_by(DestinySeasonPassDefinition.index.asc()).limit(1)

        result = await self._execute_query(db=db, query=query)
        return result.scalar()


destiny_manifest = CRUDManifest(Base)
