import datetime
import time
from typing import Optional

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import DiscordUsers
from Backend.networking.base import NetworkBase
from Backend.schemas.auth import BungieTokenInput, BungieTokenOutput
from settings import BUNGIE_TOKEN


class CRUDDiscordUser(CRUDBase):
    async def get_profile_from_discord_id(self, db: AsyncSession, discord_id: int) -> DiscordUsers:
        """Return the profile information"""

        profile: Optional[DiscordUsers] = await self._get_with_key(db, discord_id)

        # make sure the user exists
        if not profile:
            raise CustomException(
                error="DiscordIdNotFound",
            )

        return profile

    async def get_profile_from_destiny_id(self, db: AsyncSession, destiny_id: int) -> DiscordUsers:
        """Return the profile information"""

        profiles: list[DiscordUsers] = await self._get_multi_with_filter(db, destiny_id=destiny_id)

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
        api = NetworkBase()

        # get the corresponding destiny data with manual headers, since the data is not in the db yet
        async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
            destiny_info = await api._get_request(
                session=session,
                route="https://www.bungie.net/platform/User/GetMembershipsForCurrentUser/",
                headers={
                    "X-API-Key": BUNGIE_TOKEN,
                    "Accept": "application/json",
                    "Authorization": f"Bearer {bungie_token.access_token}",
                },
            )

        # get the users destiny info
        destiny_id = int(destiny_info.content["primaryMembershipId"])

        # get the system
        system = None
        for profile in destiny_info.content["destinyMemberships"]:
            if int(profile["membershipId"]) == destiny_id:
                system = profile["membershipType"]
                break

        # that should find a system 100% of the time, extra check here to be sure
        if not system:
            return BungieTokenOutput(
                success=False,
                errror_message="Could not find what platform you are on",
            )

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
            user = DiscordUsers(
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
        user: DiscordUsers,
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

    async def get_join_id(self, db: AsyncSession, discord_id: int) -> int:
        """Gets a join id from the DB"""

        profile = await self.get_profile_from_discord_id(db=db, discord_id=discord_id)
        join_id = profile.steam_join_id

        if not join_id:
            raise CustomException("NoJoinId")

        return join_id

    async def update_join_id(self, db: AsyncSession, discord_id: int, new_join_id: int) -> int:
        """Updates a join id from the DB"""

        profile = await self.get_profile_from_discord_id(db=db, discord_id=discord_id)

        # update it
        await self._update(db=db, to_update=profile, steam_join_id=new_join_id)

        return profile.steam_join_id

    async def delete_join_id(self, db: AsyncSession, discord_id: int):
        """Deletes a join id from the DB"""

        profile = await self.get_profile_from_discord_id(db=db, discord_id=discord_id)

        # is an id even set?
        if not profile.steam_join_id:
            return

        # update it
        await self._update(db=db, to_update=profile, steam_join_id=None)


discord_users = CRUDDiscordUser(DiscordUsers)
