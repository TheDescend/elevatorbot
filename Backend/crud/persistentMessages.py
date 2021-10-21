from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.crud.cache import cache
from Backend.database.models import PersistentMessage


class CRUDPersistentMessages(CRUDBase):
    cache = cache

    async def get(self, db: AsyncSession, guild_id: int, message_name: str) -> PersistentMessage:
        """Get the persistent message"""

        # populate cache
        cache_str = f"{guild_id}|{message_name}"
        if cache_str not in self.cache.persistent_messages:
            self.cache.persistent_messages.update(
                {cache_str: await self._get_with_key(db=db, primary_key=(message_name, guild_id))}
            )

        return self.cache.persistent_messages[cache_str]

    async def upsert(
        self, db: AsyncSession, guild_id: int, message_name: str, channel_id: int = None, message_id: int = None
    ) -> PersistentMessage:
        """Upsert the persistent message"""

        # convert kwargs into dict
        upsert_dict = {
            "message_name": message_name,
            "guild_id": guild_id,
        }
        if channel_id:
            upsert_dict.update({"channel_id": channel_id})
        if message_id:
            upsert_dict.update({"message_id": message_id})

        model = await self._upsert(db=db, model_data=upsert_dict)

        # place model in cache
        cache_str = f"{guild_id}|{message_name}"
        self.cache.persistent_messages.update({cache_str: model})

        return model

    async def delete(self, db: AsyncSession, guild_id: int, message_name: str):
        """Delete the persistent message"""

        await self._delete(db=db, primary_key=(message_name, guild_id))

        # delete from cache
        cache_str = f"{guild_id}|{message_name}"
        try:
            self.cache.persistent_messages.pop(cache_str)
        except KeyError:
            pass


persistent_messages = CRUDPersistentMessages(PersistentMessage)
