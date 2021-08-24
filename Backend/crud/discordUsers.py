import datetime
import time
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import DiscordGuardiansToken
from Backend.networking.bungieApi import BungieApi
from Backend.schemas.auth import BungieTokenInput, BungieTokenOutput


class CRUDDiscordUser(CRUDBase):
    async def get_profile_from_discord_id(self, db: AsyncSession, discord_id: int) -> DiscordGuardiansToken:
        """Return the profile information"""

        profile: Optional[DiscordGuardiansToken] = await self._get_with_key(db, discord_id)

        # make sure the user exists
        if not profile:
            raise CustomException(
                error="DiscordIdNotFound",
            )

        return profile

    async def get_profile_from_destiny_id(self, db: AsyncSession, destiny_id: int) -> DiscordGuardiansToken:
        """Return the profile information"""

        profiles: list[DiscordGuardiansToken] = await self._get_multi_with_filter(db, destiny_id=destiny_id)

        # make sure the user exists
        if not profiles:
            raise CustomException(
                error="DestinyIdNotFound",
            )

        return profiles[0]

    async def insert_profile(self, db: AsyncSession, bungie_token: BungieTokenInput) -> BungieTokenOutput:
        """Inserts a users token data"""

        # get current time
        current_time = int(time.time())

        # split the state
        (discord_id, guild_id, channel_id) = bungie_token.state.split(":")
        discord_id, guild_id, channel_id, = (
            int(discord_id),
            int(guild_id),
            int(channel_id),
        )
        api = BungieApi(discord_id=discord_id)

        # get the corresponding destiny data
        destiny_info = await api.get_json_from_bungie_with_token(
            db=db,
            route="https://www.bungie.net/platform/User/GetMembershipsForCurrentUser/",
        )

        # todo change to new destiny name system since thats universal and should hopefully only have one id / system
        # get the users destiny info
        destiny_id = None
        system = None
        for profile in destiny_info.content["destinyMemberships"]:
            destiny_id = int(profile["membershipId"])
            system = profile["membershipType"]

            # if there is no cross save data, prefer pc
            if "crossSaveOverride" not in profile and profile["membershipType"] == 3:
                break

            # cross save data is preferred
            if "crossSaveOverride" in profile and (profile["crossSaveOverride"] == profile["membershipType"]):
                break

        # if they have no destiny profile
        if not destiny_id:
            return BungieTokenOutput(
                success=False,
                errror_message="You do not seem to have a destiny account",
            )

        # look if that destiny_id is already in the db
        try:
            user = await self.get_profile_from_destiny_id(db=db, destiny_id=destiny_id)

            # if that returned something, we need to make sure the destiny_id belongs to the same discord_id
            if not user.discord_id == discord_id:
                # if it doesnt, we need to delete that entry, otherwise a destiny account could be registered to multiple persons
                await self.delete_profile(db=db, discord_id=user.discord_id)

                # now we gotta make it an insert instead of an update
                method_insert = True

            else:
                # if they are the same, we need to update the obj instead of inserting it
                method_insert = False

        except CustomException:
            # if this triggers we know no result was found in the db, so we insert
            method_insert = True

        if method_insert:
            # new user! so lets construct their info
            user = DiscordGuardiansToken(
                discord_id=discord_id,
                destiny_id=destiny_id,
                system=system,
                token=bungie_token.access_token,
                refresh_token=bungie_token.refresh_token,
                token_expiry=datetime.datetime.fromtimestamp(current_time + bungie_token.expires_in),
                refresh_token_expiry=datetime.datetime.fromtimestamp(current_time + bungie_token.refresh_expires_in),
                signup_date=datetime.date.today(),
                signup_server_id=guild_id,
            )

            # and in the db they go
            await self._insert(db=db, to_create=user)

        else:
            # now we call the update function instead of the insert function
            await self._update(
                db=db,
                to_update=user,
                destiny_id=destiny_id,
                system=system,
                token=bungie_token.access_token,
                refresh_token=bungie_token.refresh_token,
                token_expiry=datetime.datetime.fromtimestamp(current_time + bungie_token.expires_in),
                refresh_token_expiry=datetime.datetime.fromtimestamp(current_time + bungie_token.refresh_expires_in),
            )

        # todo connect to the websocket on elevator for them to write a message

        return BungieTokenOutput(success=True, errror_message=None)

    async def refresh_tokens(
        self,
        db: AsyncSession,
        user: DiscordGuardiansToken,
        token=str,
        refresh_token=str,
        token_expiry=datetime,
        refresh_token_expiry=datetime,
    ):
        """Updates a profile (token refreshes)"""

        await self._update(
            db=db,
            to_update=user,
            token=token,
            refresh_token=refresh_token,
            token_expiry=token_expiry,
            refresh_token_expiry=refresh_token_expiry,
        )

    async def delete_profile(self, db: AsyncSession, discord_id: int):
        """Deletes the profile from the DB"""

        result = await self._delete(db=db, primary_key=discord_id)

        if not result:
            raise CustomException(
                error="DiscordIdNotFound",
            )


discord_users = CRUDDiscordUser(DiscordGuardiansToken)
