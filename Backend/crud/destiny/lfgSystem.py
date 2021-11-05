from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import LfgMessage


class CRUDLfgMessages(CRUDBase):
    async def insert(self, db: AsyncSession, to_create: LfgMessage):
        """Inserts the lfg info and gives it a new id"""

        await self._insert(db=db, to_create=to_create)

    async def get(self, db: AsyncSession, lfg_id: int, guild_id: int) -> LfgMessage:
        """Get the lfg info for the guild"""

        result = await self._get_with_key(db=db, primary_key=lfg_id)

        # check exists and guild
        if (not result) or (result.guild_id != guild_id):
            raise CustomException("NoLfgEventWithIdForGuild")

        return result

    async def get_all(self, db: AsyncSession, guild_id: int) -> list[LfgMessage]:
        """Get the lfg info for the guild"""

        return await self._get_multi(db=db, guild_id=guild_id)

    async def delete(self, db: AsyncSession, lfg_id: int, guild_id: int, discord_id: int):
        """Delete the lfg info belonging to the lfg id and guild"""

        obj = await self.get(db=db, lfg_id=lfg_id, guild_id=guild_id)

        # check author
        await self._check_author(obj=obj, discord_id=discord_id)

        await self._delete(db=db, obj=obj)

    async def update(self, db: AsyncSession, lfg_id: int, guild_id: int, discord_id: int, **update_data) -> LfgMessage:
        """Update the lfg info belonging to the lfg id and guild"""

        obj = await self.get(db=db, lfg_id=lfg_id, guild_id=guild_id)

        # check author
        await self._check_author(obj=obj, discord_id=discord_id)

        # remove none values
        update_data = {k: v for k, v in update_data.items() if v is not None}

        await self._update(db=db, to_update=obj, **update_data)

        return obj

    @staticmethod
    async def _check_author(obj: LfgMessage, discord_id: int):
        """Checks if the discord_id is the creator"""

        if obj.author_id != discord_id:
            raise CustomException("NoLfgEventPermissions")


lfg = CRUDLfgMessages(LfgMessage)
