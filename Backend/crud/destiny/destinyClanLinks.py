import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import DestinyClanLinks


class CRUDDestinyClanLinks(CRUDBase):
    async def get_link(
        self,
        db: AsyncSession,
        discord_guild_id: int,
    ) -> Optional[DestinyClanLinks]:
        """Gets the discord guilds linked clan"""

        return await self._get_with_key(db, discord_guild_id)

    async def link(self, db: AsyncSession, discord_id: int, discord_guild_id: int, destiny_clan_id: int):
        """Insert a clan link"""

        # check if the destiny guild is already linked to a discord server
        link = await self._get_multi_with_filter(db, discord_guild_id)
        if link:
            # if it does we need to delete that, since a destiny clan can only get linked to one discord guild
            await self._delete(db, obj=link[0])

        # check if a link to a different destiny clan exists
        link = await self.get_link(db, discord_guild_id)
        if link:
            # now we need to update and not insert
            await self._update(
                db=db,
                to_update=link,
                destiny_clan_id=destiny_clan_id,
                link_date=datetime.datetime.now(),
                linked_by_discord_id=discord_id,
            )

        else:
            # insert clan link
            await self._insert(
                db=db,
                to_create=DestinyClanLinks(
                    discord_guild_id=discord_guild_id,
                    to_update=link,
                    destiny_clan_id=destiny_clan_id,
                    link_date=datetime.datetime.now(tz=datetime.timezone.utc),
                    linked_by_discord_id=discord_id,
                ),
            )

    async def unlink(
        self,
        db: AsyncSession,
        discord_guild_id: int,
    ):
        """Delete a clan link"""

        await self._delete(db, primary_key=discord_guild_id)


destiny_clan_links = CRUDDestinyClanLinks(DestinyClanLinks)
