from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import (
    DestinyCollectibleDefinition,
    DestinyInventoryItemDefinition,
    DestinyPresentationNodeDefinition,
    DestinyRecordDefinition,
)
from Backend.misc.cache import cache
from DestinyEnums.enums import DestinyPresentationNodesEnum


class CRUDDestinyItems(CRUDBase):
    async def get_all_weapons(self, db: AsyncSession) -> list[DestinyInventoryItemDefinition]:
        """Return all weapons"""

        # item_type == 3 -> weapons
        return await self._get_multi(db=db, item_type=3)

    async def get_item(self, db: AsyncSession, item_id: int) -> Optional[DestinyInventoryItemDefinition]:
        """Return the item"""

        # check cache
        if item_id not in cache.items:
            cache.items.update({item_id: await self._get_with_key(db=db, primary_key=item_id)})

        return cache.items[item_id]

    async def get_collectible(self, db: AsyncSession, collectible_id: int) -> Optional[DestinyCollectibleDefinition]:
        """Return the collectible"""

        query = select(DestinyCollectibleDefinition)
        query = query.filter(DestinyCollectibleDefinition.reference_id == collectible_id)

        results = await self._execute_query(db=db, query=query)
        result = results.scalar()

        if not result:
            raise CustomException("BungieDestinyItemNotExist")

        return result

    async def get_record(self, db: AsyncSession, record_id: int) -> DestinyRecordDefinition:
        """Return the record"""

        query = select(DestinyRecordDefinition)
        query = query.filter(DestinyRecordDefinition.reference_id == record_id)

        results = await self._execute_query(db=db, query=query)
        result = results.scalar()

        if not result:
            raise CustomException("BungieDestinyItemNotExist")

        return result

    async def get_catalysts(self, db: AsyncSession) -> list[DestinyRecordDefinition]:
        """Returns a list of the current catalysts"""

        # check cache
        if not cache.catalysts:
            query = select(DestinyRecordDefinition)
            query = query.filter(DestinyRecordDefinition.name.like(f"% Catalyst"))

            results = await self._execute_query(db=db, query=query)
            cache.catalysts = results.scalars().all()

        return cache.catalysts

    async def get_seals(
        self, db: AsyncSession
    ) -> dict[DestinyPresentationNodeDefinition, list[DestinyRecordDefinition]]:
        """Returns a list of the current seals. Returns {title_name: DestinyRecordDefinition}"""

        # check cache
        if not cache.seals:
            query = select(DestinyPresentationNodeDefinition)
            query = query.filter(
                DestinyRecordDefinition.parent_node_hashes.any(DestinyPresentationNodesEnum.SEALS.value)
            )

            results = await self._execute_query(db=db, query=query)
            seals: list[DestinyPresentationNodeDefinition] = results.scalars().all()

            # now loop through all the seals and get the record infos
            for seal in seals:
                records = []
                for record in seal.children_record_hash:
                    records.append(await self.get_record(db=db, record_id=record))

                cache.seals.update({seal: records})

        return cache.seals


destiny_items = CRUDDestinyItems(DestinyInventoryItemDefinition)
