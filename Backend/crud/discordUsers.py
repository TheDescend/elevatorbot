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
                error="NotFound",
                error_message=f"DiscordID `{discord_id}` is not registered"
            )

        return profile

    async def get_profile_from_destiny_id(self, db: AsyncSession, destiny_id: int) -> DiscordGuardiansToken:
        """ Return the profile information """

        profiles: list[DiscordGuardiansToken] = await self.get_multi_with_filter(db, destiny_id=destiny_id)

        # make sure the user exists
        if not profiles:
            raise CustomException(
                error="NotFound",
                error_message=f"DestinyID `{destiny_id}` is not registered"
            )

        # make sure there aren't multiple matches
        if len(profiles) > 1:
            raise CustomException(
                error="MultipleResults",
                error_message="There are multiple results for DestinyID `{destiny_id}`"
            )

        return profiles[0]

discord_users = CRUDDiscordUsers(DiscordGuardiansToken)
