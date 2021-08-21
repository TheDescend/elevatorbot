import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import DiscordGuardiansToken


class CRUDDiscordUsers(CRUDBase):
    async def get_profile_from_discord_id(
        self,
        db: AsyncSession,
        discord_id: int
    ) -> DiscordGuardiansToken:
        """ Return the profile information """

        profile: Optional[DiscordGuardiansToken] = await self._get_with_key(db, discord_id)

        # make sure the user exists
        if not profile:
            raise CustomException(
                error="DiscordIdNotFound",
            )

        return profile


    async def get_profile_from_destiny_id(
        self,
        db: AsyncSession,
        destiny_id: int
    ) -> DiscordGuardiansToken:
        """ Return the profile information """

        profiles: list[DiscordGuardiansToken] = await self._get_multi_with_filter(db, destiny_id=destiny_id)

        # make sure the user exists
        if not profiles:
            raise CustomException(
                error="DestinyIdNotFound",
            )

        return profiles[0]


    async def get_token_data(
        self,
        db: AsyncSession,
        discord_id: int
    ) -> DiscordGuardiansToken:
        """ Returns a users token data """

        result: Optional[DiscordGuardiansToken] = await self._get_with_key(db, discord_id)

        # look if a token exists
        if not result:
            raise CustomException(
                error="DestinyIdNotFound",
            )

        if not result.token:
            raise CustomException(
                error="NoToken",
            )

        return result


    async def update_token_data(
        self,
        db: AsyncSession,
        user: DiscordGuardiansToken,
        token: str,
        refresh_token: str,
        token_expiry: datetime.datetime,
        refresh_token_expiry: datetime.datetime,
    ):
        """ Updates a users token data """

        await self._update(
            db=db,
            to_update=user,
            token=token,
            refresh_token=refresh_token,
            token_expiry=token_expiry,
            refresh_token_expiry=refresh_token_expiry,
        )


discord_users = CRUDDiscordUsers(DiscordGuardiansToken)
