from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import ElevatorServers


class CRUDElevatorServers(CRUDBase):

    async def insert(self, db: AsyncSession, discord_guild_id: int):
        """Insert the item"""

        # look if the item exists before inserting
        if not await self._get_with_key(db, discord_guild_id):
            await self._insert(db, ElevatorServers(guild_id=discord_guild_id))

    async def delete(self, db: AsyncSession, discord_guild_id: int):
        """Delete the item"""

        await self._delete(db, primary_key=discord_guild_id)

    async def get(
        self,
        db: AsyncSession,
    ) -> list[ElevatorServers]:
        """Get all items"""
        return await self._get_multi(db)


elevator_servers = CRUDElevatorServers(ElevatorServers) #CRUDBase(ElevatorServers)
