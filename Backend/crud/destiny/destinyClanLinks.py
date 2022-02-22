from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import DestinyClanLinks
from Shared.functions.helperFunctions import get_now_with_tz


class CRUDDestinyClanLinks(CRUDBase):
    async def get_link(self, db: AsyncSession, discord_guild_id: int) -> DestinyClanLinks:
        """Gets the discord guilds linked clan"""

        result = await self._get_with_key(db, discord_guild_id)
        if result is None:
            raise CustomException("NoClanLink")

        return result

    async def link(self, db: AsyncSession, discord_id: int, discord_guild_id: int, destiny_clan_id: int):
        """Insert a clan link"""

        # check if the destiny guild is already linked to a discord server
        link = await self._get_multi(db, discord_guild_id=discord_guild_id)
        if link:
            # if it does, we need to delete that, since a destiny clan can only get linked to one discord guild
            await self._delete(db, obj=link[0])

        # check if a link to a different destiny clan exists
        try:
            link = await self.get_link(db, discord_guild_id)

            # now we need to update and not insert
            await self._update(
                db=db,
                to_update=link,
                destiny_clan_id=destiny_clan_id,
                link_date=get_now_with_tz(),
                linked_by_discord_id=discord_id,
            )
        except CustomException:
            # insert clan link
            await self._insert(
                db=db,
                to_create=DestinyClanLinks(
                    discord_guild_id=discord_guild_id,
                    destiny_clan_id=destiny_clan_id,
                    link_date=get_now_with_tz(),
                    linked_by_discord_id=discord_id,
                ),
            )

    async def unlink(self, db: AsyncSession, discord_guild_id: int):
        """Delete a clan link"""

        await self._delete(db, primary_key=discord_guild_id)


destiny_clan_links = CRUDDestinyClanLinks(DestinyClanLinks)
