from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.crud.cache import cache
from Backend.database.models import PersistentMessage
from Backend.misc.helperFunctions import convert_kwargs_into_dict


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

    async def delete(self, db: AsyncSession, guild_id: int, message_name: str):
        """Delete the persistent message"""

        await self._delete(db=db, primary_key=(message_name, guild_id))

        # delete from cache
        cache_str = f"{guild_id}|{message_name}"
        try:
            self.cache.persistent_messages.pop(cache_str)
        except KeyError:
            pass

    async def get_registration_roles(self, db: AsyncSession, guild_id: Optional[int] = None) -> list[PersistentMessage]:
        """Get the registered role (channel_id)"""

        if guild_id:
            result = await self.get(db=db, guild_id=guild_id, message_name="registered_role")
            return [result]

        else:
            return await self._get_multi(db=db, message_name="registered_role")


persistent_messages = CRUDPersistentMessages(PersistentMessage)
