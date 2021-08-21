from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import DiscordGuardiansToken


class CRUDDiscordUsers(CRUDBase):
    async def get_profile_from_discord_id(self, db: AsyncSession, discord_id: int) -> DiscordGuardiansToken:
        """ Return the profile information """

        profile: Optional[DiscordGuardiansToken] = await self.get_with_key(db, discord_id)

        # make sure the user exists
        if not profile:
            raise CustomException(
                error="DiscordIdNotFound",
            )

        return profile

    async def get_profile_from_destiny_id(self, db: AsyncSession, destiny_id: int) -> DiscordGuardiansToken:
        """ Return the profile information """

        profiles: list[DiscordGuardiansToken] = await self.get_multi_with_filter(db, destiny_id=destiny_id)

        # make sure the user exists
        if not profiles:
            raise CustomException(
                error="DestinyIdNotFound",
            )


        return profiles[0]


discord_users = CRUDDiscordUsers(DiscordGuardiansToken)
