from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import RssFeedItem


class CRUDRssFeed(CRUDBase):
    async def get(self, db: AsyncSession, item_id: str) -> Optional[RssFeedItem]:
        """Return the db entry if exists"""

        return await self._get_with_key(db=db, primary_key=str(item_id))

    async def insert(self, db: AsyncSession, item_id: str):
        """Insert the rss feed item id in the db"""

        return await self._insert(db=db, to_create=RssFeedItem(id=str(item_id)))


rss_feed = CRUDRssFeed(RssFeedItem)
