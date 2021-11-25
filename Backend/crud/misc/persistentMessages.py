from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import PersistentMessage
from Backend.misc.cache import cache
from Backend.misc.helperFunctions import convert_kwargs_into_dict
from NetworkingSchemas.misc.persistentMessages import PersistentMessageDeleteInput


class CRUDPersistentMessages(CRUDBase):
    cache = cache

    async def get(self, db: AsyncSession, guild_id: int, message_name: str) -> PersistentMessage:
        """Get the persistent message"""

        # populate cache
        cache_str = f"{guild_id}|{message_name}"
        if cache_str not in self.cache.persistent_messages:
            result = await self._get_with_key(db=db, primary_key=(message_name, guild_id))
            if not result:
                raise CustomException("PersistentMessageNotExist")

            self.cache.persistent_messages.update({cache_str: result})

        return self.cache.persistent_messages[cache_str]

    async def get_all(self, db: AsyncSession, message_name: str) -> list[PersistentMessage]:
        """Get the persistent message for all guilds"""

        # not using cache for that since we dont know all guild_ids
        return await self._get_multi(db=db, message_name=message_name)

    async def upsert(
        self,
        db: AsyncSession,
        guild_id: int,
        message_name: str,
        channel_id: Optional[int] = None,
        message_id: Optional[int] = None,
    ) -> PersistentMessage:
        """Upsert the persistent message"""

        # convert kwargs into dict
        upsert_dict = {
            "message_name": message_name,
            "guild_id": guild_id,
        }
        upsert_dict.update(
            convert_kwargs_into_dict(
                channel_id=channel_id,
                message_id=message_id,
            )
        )

        model = await self._upsert(db=db, model_data=upsert_dict)

        # place model in cache
        cache_str = f"{guild_id}|{message_name}"
        self.cache.persistent_messages.update({cache_str: model})

        return model

    async def delete(self, db: AsyncSession, guild_id: int, to_delete: PersistentMessageDeleteInput):
        """Delete the persistent message"""

        if to_delete.message_name:
            objs = [await self._delete(db=db, primary_key=(to_delete.message_name, guild_id))]
        elif to_delete.channel_id:
            objs = await self._delete_multi(db=db, guild_id=guild_id, channel_id=to_delete.channel_id)
        else:
            objs = await self._delete_multi(db=db, guild_id=guild_id, message_id=to_delete.message_id)

        # delete from cache
        for obj in objs:
            cache_str = f"{guild_id}|{obj.message_name}"
            try:
                self.cache.persistent_messages.pop(cache_str)
            except KeyError:
                pass

    async def delete_all(self, db: AsyncSession, guild_id: int):
        """Deletes all persistent message for a guild"""

        await self._delete_multi(db=db, guild_id=guild_id)

        # delete from cache
        for key in list(self.cache.persistent_messages.keys()):
            if key.startswith(str(guild_id)):
                self.cache.persistent_messages.pop(key)

    async def get_registration_roles(self, db: AsyncSession, guild_id: Optional[int] = None) -> list[PersistentMessage]:
        """Get the registered role (channel_id)"""

        if guild_id:
            result = await self.get(db=db, guild_id=guild_id, message_name="registered_role")
            return [result]

        else:
            return await self._get_multi(db=db, message_name="registered_role")


persistent_messages = CRUDPersistentMessages(PersistentMessage)
