import datetime
import time
from typing import Optional

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.crud.discord.roles import roles
from Backend.crud.misc.persistentMessages import persistent_messages
from Backend.database.models import DiscordUsers
from Backend.misc.cache import cache
from Backend.misc.helperFunctions import get_now_with_tz, localize_datetime
from Backend.networking.base import NetworkBase
from Backend.networking.elevatorApi import ElevatorApi
from NetworkingSchemas.misc.auth import BungieTokenInput, BungieTokenOutput
from settings import BUNGIE_APPLICATION_API_KEY


class CRUDDiscordUser(CRUDBase):
    cache = cache

    async def get_profile_from_discord_id(self, db: AsyncSession, discord_id: int) -> DiscordUsers:
        """Return the profile information"""

        # check if exists in cache
        if discord_id in self.cache.discord_users:
            return self.cache.discord_users[discord_id]

        profile: Optional[DiscordUsers] = await self._get_with_key(db, discord_id)

        # make sure the user exists
        if not profile:
            raise CustomException(error="DiscordIdNotFound")

        # populate cache
        self.cache.discord_users.update({discord_id: profile})

        return profile

    async def get_profile_from_destiny_id(self, db: AsyncSession, destiny_id: int) -> DiscordUsers:
        """Return the profile information"""

        profiles: list[DiscordUsers] = await self._get_multi(db, destiny_id=destiny_id)

        # make sure the user exists
        if not profiles:
            raise CustomException(error="DestinyIdNotFound")

        return profiles[0]

    async def get_all(self, db: AsyncSession) -> list[DiscordUsers]:
        """Return all profiles"""

        return await self._get_all(db=db)

    async def insert_profile(
        self, db: AsyncSession, bungie_token: BungieTokenInput
    ) -> tuple[BungieTokenOutput, Optional[DiscordUsers], int, int]:
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
            destiny_info = await api._request(
                session=session,
                method="GET",
                route="https://www.bungie.net/platform/User/GetMembershipsForCurrentUser/",
                headers={
                    "X-API-Key": BUNGIE_APPLICATION_API_KEY,
                    "Accept": "application/json",
                    "Authorization": f"Bearer {bungie_token.access_token}",
                },
            )

        # get the user's destiny info
        destiny_id = int(destiny_info.content.get("primaryMembershipId"))
        if not destiny_id:
            #if primary is not defined, there is only one
            memberships = destiny_info.content["destinyMemberships"]
            assert(len(memberships) == 1)
            destiny_id = int(memberships[0]["membershipId"])

        # get the system
        system = None
        bungie_name = None
        for profile in destiny_info.content["destinyMemberships"]:
            if int(profile["membershipId"]) == destiny_id:
                system = profile["membershipType"]
                bungie_name = f"""{profile["bungieGlobalDisplayName"]}#{profile["bungieGlobalDisplayNameCode"]}"""
                break

        # that should find a system 100% of the time, extra check here to be sure
        if not system:
            return (
                BungieTokenOutput(success=False, errror_message="Could not find what platform you are on"),
                None,
                discord_id,
                guild_id,
            )

        # if they have no destiny profile
        if not destiny_id:
            return (
                BungieTokenOutput(success=False, errror_message="You do not seem to have a destiny account"),
                None,
                discord_id,
                guild_id,
            )

        # look if that destiny_id is already in the db
        try:
            user = await self.get_profile_from_destiny_id(db=db, destiny_id=destiny_id)

            # if that returned something, we need to make sure the destiny_id belongs to the same discord_id
            if not user.discord_id == discord_id:
                # if it doesn't, we need to delete that entry, otherwise a destiny account could be registered to multiple persons
                await self.delete_profile(db=db, discord_id=user.discord_id)

                # now we have to make it an insert instead of an update
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
                bungie_name=bungie_name,
                token=bungie_token.access_token,
                refresh_token=bungie_token.refresh_token,
                token_expiry=localize_datetime(datetime.datetime.fromtimestamp(current_time + bungie_token.expires_in)),
                refresh_token_expiry=localize_datetime(
                    datetime.datetime.fromtimestamp(current_time + bungie_token.refresh_expires_in)
                ),
                signup_date=get_now_with_tz(),
                signup_server_id=guild_id,
            )

            # and in the db they go
            await self._insert(db=db, to_create=user)

            # populate the cache
            self.cache.discord_users.update({discord_id: user})

        else:
            # now we call the update function instead of the insert function
            datetime_default = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
            await self.update(
                db=db,
                to_update=user,
                destiny_id=destiny_id,
                system=system,
                bungie_name=bungie_name,
                token=bungie_token.access_token,
                refresh_token=bungie_token.refresh_token,
                token_expiry=localize_datetime(datetime.datetime.fromtimestamp(current_time + bungie_token.expires_in)),
                refresh_token_expiry=localize_datetime(
                    datetime.datetime.fromtimestamp(current_time + bungie_token.refresh_expires_in)
                ),
                activities_last_updated=datetime_default,
                collectibles_last_updated=datetime_default,
                triumphs_last_updated=datetime_default,
            )

        return BungieTokenOutput(success=True, errror_message=None), user, discord_id, guild_id

    async def update(self, db: AsyncSession, to_update: DiscordUsers, **update_kwargs):
        """Updates a profile"""

        await self._update(db=db, to_update=to_update, **update_kwargs)

        # update the cache
        self.cache.discord_users.update({to_update.discord_id: to_update})

    async def invalidate_token(self, db: AsyncSession, user: DiscordUsers):
        """Invalidates a token by setting it to None"""

        await self.update(
            db=db,
            to_update=user,
            token=None,
        )

        # remove registration roles
        await self.remove_registration_roles(db=db, discord_id=user.discord_id)

    async def token_is_expired(self, db: AsyncSession, user: DiscordUsers):
        """Checks if a token exists and the refresh token is not expired"""

        if not user.token:
            return True

        current_time = get_now_with_tz()
        if current_time > user.refresh_token_expiry:
            # set token to None
            await self.invalidate_token(db=db, user=user)

            return True

        return False

    async def delete_profile(self, db: AsyncSession, discord_id: int):
        """Deletes the profile from the DB"""

        result = await self._delete(db=db, primary_key=discord_id)

        if not result:
            raise CustomException(
                error="DiscordIdNotFound",
            )

        # delete from cache
        try:
            self.cache.discord_users.pop(discord_id)
        except KeyError:
            pass

        # remove registration roles
        await self.remove_registration_roles(db=db, discord_id=discord_id)

    @staticmethod
    async def remove_registration_roles(db: AsyncSession, discord_id: int, guild_ids: Optional[list[int]] = None):
        """Removes registration roles from user in all guilds"""

        # loop through guilds to remove registration info from the user
        data = []
        role_data = await persistent_messages.get_registration_roles(db=db)
        for role in role_data:
            guild_id = role.guild_id
            registered_role_id = role.channel_id

            if guild_ids:
                if guild_id not in guild_ids:
                    continue

            # append that to the data we're gonna send elevator
            data.append(
                {
                    "discord_id": discord_id,
                    "guild_id": guild_id,
                    "to_assign_role_ids": None,
                    "to_remove_role_ids": [registered_role_id],
                }
            )

        # send elevator that data to apply the roles
        if data:
            elevator_api = ElevatorApi()
            await elevator_api.post(
                route_addition="roles/",
                json={
                    "data": data,
                },
            )

    @staticmethod
    async def add_registration_roles(db: AsyncSession, discord_id: int, guild_ids: Optional[list[int]] = None):
        """Add registration roles to user in all guilds"""

        # loop through guilds to remove registration info from the user
        data = []
        role_data = await persistent_messages.get_registration_roles(db=db)
        for role in role_data:
            guild_id = role.guild_id
            registered_role_id = role.channel_id

            if guild_ids:
                if guild_id not in guild_ids:
                    continue

            # append that to the data we're gonna send elevator
            data.append(
                {
                    "discord_id": discord_id,
                    "guild_id": guild_id,
                    "to_assign_role_ids": [registered_role_id],
                    "to_remove_role_ids": None,
                }
            )

        # send elevator that data to apply the roles
        if data:
            elevator_api = ElevatorApi()
            await elevator_api.post(
                route_addition="roles/",
                json={
                    "data": data,
                },
            )


discord_users = CRUDDiscordUser(DiscordUsers)
