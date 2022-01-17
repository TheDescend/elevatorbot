import asyncio
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.crud.misc.persistentMessages import persistent_messages
from Backend.database.models import LfgMessage
from Backend.misc.cache import cache
from Shared.networkingSchemas.destiny.lfgSystem import AllLfgDeleteOutputModel, LfgOutputModel, UserAllLfgOutputModel


class CRUDLfgMessages(CRUDBase):
    @staticmethod
    async def get_channel_id(db: AsyncSession, guild_id: int) -> int:
        """Return the guild's lfg channel id"""

        # check cache:
        async with asyncio.Lock():
            cache_key = f"{guild_id}|lfg_channel"

            # populate cache
            if cache_key not in cache.persistent_messages:
                try:
                    await persistent_messages.get(db=db, guild_id=guild_id, message_name="lfg_channel")
                except CustomException as e:
                    if e.error == "PersistentMessageNotExist":
                        cache.persistent_messages.update({cache_key: None})
                    else:
                        raise e

            result = cache.persistent_messages[cache_key]
            if not result:
                raise CustomException("NoLfgChannelForGuild")
            return result.channel_id if result else None

    @staticmethod
    async def get_voice_category_channel_id(db: AsyncSession, guild_id: int) -> Optional[int]:
        """Return the guild's lfg voice category channel id if set"""

        # check cache:
        async with asyncio.Lock():
            cache_key = f"{guild_id}|lfg_voice_category"

            # populate cache
            if cache_key not in cache.persistent_messages:
                try:
                    await persistent_messages.get(db=db, guild_id=guild_id, message_name="lfg_voice_category")
                except CustomException as e:
                    if e.error == "PersistentMessageNotExist":
                        cache.persistent_messages.update({cache_key: None})
                    else:
                        raise e

            result = cache.persistent_messages[cache_key]
            return result.channel_id if result else None

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

    async def get_user(self, db: AsyncSession, discord_id: int, guild_id: int) -> UserAllLfgOutputModel:
        """Get the lfg infos for the user"""

        voice_category_channel_id = await self.get_voice_category_channel_id(db=db, guild_id=guild_id)

        result = UserAllLfgOutputModel()

        joined = await self._get_user_events(db=db, discord_id=discord_id, joined=True)
        result.joined = [LfgOutputModel.from_orm(obj) for obj in joined]
        for entry in result.joined:
            entry.voice_category_channel_id = voice_category_channel_id

        backup = await self._get_user_events(db=db, discord_id=discord_id, backup=True)
        result.backup = [LfgOutputModel.from_orm(obj) for obj in backup]
        for entry in result.backup:
            entry.voice_category_channel_id = voice_category_channel_id

        return result

    async def delete(self, db: AsyncSession, lfg_id: int, guild_id: int, discord_id: int):
        """Delete the lfg info belonging to the lfg id and guild"""

        obj = await self.get(db=db, lfg_id=lfg_id, guild_id=guild_id)

        # check author
        await self._check_author(obj=obj, discord_id=discord_id)

        await self._delete(db=db, obj=obj)

    async def delete_all(self, db: AsyncSession, guild_id: int) -> AllLfgDeleteOutputModel:
        """Delete all lfg events for the guild"""

        objs: list[LfgMessage] = await self._delete_multi(db=db, guild_id=guild_id)
        return AllLfgDeleteOutputModel(event_ids=[obj.id for obj in objs])

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

        if discord_id != 1:
            if obj.author_id != discord_id:
                raise CustomException("NoLfgEventPermissions")

    async def _get_user_events(
        self, db: AsyncSession, discord_id: int, joined: bool = False, backup: bool = False
    ) -> list[LfgMessage]:
        """Get the lfg infos for the user"""

        query = select(LfgMessage)

        if joined:
            query = query.filter(LfgMessage.joined_members.any(discord_id))
        if backup:
            query = query.filter(LfgMessage.backup_members.any(discord_id))

        result = await self._execute_query(db, query)
        return result.scalars().fetchall()


lfg = CRUDLfgMessages(LfgMessage)
