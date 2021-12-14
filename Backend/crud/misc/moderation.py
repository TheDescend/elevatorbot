import datetime
from enum import Enum
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import ModerationLog
from Backend.misc.helperFunctions import get_now_with_tz


class ModerationTypes(Enum):
    WARNING = "warning"
    MUTE = "mute"


class CRUDModeration(CRUDBase):
    async def get(
        self, db: AsyncSession, discord_id: int, guild_id: int, mod_type: ModerationTypes
    ) -> list[ModerationLog]:
        """Get the users past offenses"""

        return await self._get_multi(db=db, guild_id=guild_id, discord_id=discord_id, type=mod_type.value)

    async def add(
        self,
        db: AsyncSession,
        discord_id: int,
        guild_id: int,
        mod_discord_id: int,
        mod_type: ModerationTypes,
        reason: str,
        duration_in_seconds: Optional[int] = None,
    ) -> ModerationLog:
        """Add an offense to a user"""

        model = ModerationLog(
            guild_id=guild_id,
            discord_id=discord_id,
            mod_discord_id=mod_discord_id,
            type=mod_type.value,
            duration_in_seconds=duration_in_seconds,
            reason=reason,
            date=get_now_with_tz(),
        )

        await self._insert(db=db, to_create=model)
        return model


moderation = CRUDModeration(ModerationLog)
