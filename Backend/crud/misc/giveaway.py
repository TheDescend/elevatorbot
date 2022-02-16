from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import Giveaway


class CRUDGiveaway(CRUDBase):
    async def get(self, db: AsyncSession, giveaway_id: int) -> Giveaway:
        """Get the giveaway"""

        giveaway = await self._get_with_key(db=db, primary_key=giveaway_id)

        if not giveaway:
            raise CustomException("NoGiveaway")

        return giveaway

    async def create(self, db: AsyncSession, giveaway_id: int, author_id: int, guild_id: int):
        """Create the giveaway"""

        to_create = Giveaway(message_id=giveaway_id, author_id=author_id, guild_id=guild_id, discord_ids=[])
        await self._insert(db=db, to_create=to_create)

    async def insert(self, db: AsyncSession, giveaway_id: int, discord_id: int) -> Giveaway:
        """Insert a user in the giveaway"""

        giveaway = await self.get(db=db, giveaway_id=giveaway_id)
        if discord_id in giveaway.discord_ids:
            raise CustomException("AlreadyInGiveaway")

        giveaway.discord_ids.append(discord_id)
        flag_modified(giveaway, "discord_ids")
        return await self._update(db=db, to_update=giveaway)

    async def remove(self, db: AsyncSession, giveaway_id: int, discord_id: int) -> Giveaway:
        """Remove a user from the giveaway"""

        giveaway = await self.get(db=db, giveaway_id=giveaway_id)
        if discord_id in giveaway.discord_ids:
            giveaway.discord_ids.remove(discord_id)
            flag_modified(giveaway, "discord_ids")
            await self._update(db=db, to_update=giveaway)

        return giveaway


crud_giveaway = CRUDGiveaway(Giveaway)
