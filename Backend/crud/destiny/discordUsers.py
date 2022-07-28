import asyncio
import copy
import urllib.parse
from contextlib import AsyncExitStack
from typing import Optional

from bungio.models import AuthData
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.crud.misc.persistentMessages import persistent_messages
from Backend.database.base import acquire_db_session
from Backend.database.models import DiscordUsers
from Backend.misc.cache import cache
from Backend.networking.elevatorApi import ElevatorApi
from Shared.enums.elevator import DestinySystemEnum
from Shared.functions.helperFunctions import get_min_with_tz, get_now_with_tz
from Shared.networkingSchemas.misc.auth import BungieTokenOutput

insert_profile_lock = asyncio.Lock()
update_lock = asyncio.Lock()


class CRUDDiscordUser(CRUDBase):
    """Database interface for DiscordUser Manipulation"""

    cache = cache

    async def get_profile_from_discord_id(self, discord_id: int, db: AsyncSession = None) -> DiscordUsers:
        """Return the profile information"""

        # check if exists in cache
        if discord_id in self.cache.discord_users:
            return self.cache.discord_users[discord_id]

        async with AsyncExitStack() as async_onexit_calls:
            if db is None:
                db = await async_onexit_calls.enter_async_context(acquire_db_session())
            profile: Optional[DiscordUsers] = await self._get_with_key(db, discord_id)

            # make sure the user exists
            if not profile:
                raise CustomException(error="DiscordIdNotFound")

            profile = copy.deepcopy(profile)

            # populate cache
            self.cache.discord_users.update({discord_id: profile})
            self.cache.discord_users_by_destiny_id.update({profile.destiny_id: profile})

            return profile
            # context-manager calls session.close

    async def get_profile_from_destiny_id(self, db: AsyncSession, destiny_id: int) -> DiscordUsers:
        """Return the profile information"""

        # check if exists in cache
        if destiny_id in self.cache.discord_users_by_destiny_id:
            return self.cache.discord_users_by_destiny_id[destiny_id]

        profiles: list[DiscordUsers] = await self._get_multi(db, destiny_id=destiny_id)

        # make sure the user exists
        if not profiles:
            raise CustomException(error="DestinyIdNotFound")

        # populate cache
        self.cache.discord_users.update({profiles[0].discord_id: profiles[0]})
        self.cache.discord_users_by_destiny_id.update({profiles[0].destiny_id: profiles[0]})

        return profiles[0]

    async def get_all(self, db: AsyncSession) -> list[DiscordUsers]:
        """Return all profiles"""

        return await self._get_all(db=db)

    async def insert_profile(
        self, db: AsyncSession, auth: AuthData, state: str
    ) -> tuple[BungieTokenOutput, Optional[DiscordUsers], int, int]:
        """Inserts a users token data"""

        # make sure the state is not url encoded
        state = urllib.parse.unquote(state)

        # split the state
        (discord_id, guild_id, channel_id) = state.split(":")
        discord_id, guild_id, channel_id, = (
            int(discord_id),
            int(guild_id),
            int(channel_id),
        )

        if not auth.bungie_name:
            raise CustomException("No Bungie Name found, please launch the game")

        # if they have no destiny profile
        if not auth.membership_id:
            raise CustomException("BungieNoDestinyId")

        # need to make this save
        async with insert_profile_lock:
            # look if that destiny_id is already in the db
            try:
                user = await self.get_profile_from_destiny_id(db=db, destiny_id=auth.membership_id)

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
                    destiny_id=auth.membership_id,
                    system=auth.membership_type.value,
                    bungie_name=auth.bungie_name,
                    token=auth.token,
                    refresh_token=auth.refresh_token,
                    token_expiry=auth.token_expiry,
                    refresh_token_expiry=auth.refresh_token_expiry,
                    signup_date=get_now_with_tz(),
                    signup_server_id=guild_id,
                )

                # and in the db they go
                await self._insert(db=db, to_create=user)

                # populate the cache
                self.cache.discord_users.update({discord_id: user})
                self.cache.discord_users_by_destiny_id.update({user.destiny_id: user})

            else:
                # now we call the update function instead of the insert function
                datetime_default = get_min_with_tz()
                await self.update(
                    db=db,
                    to_update=user,
                    destiny_id=auth.membership_id,
                    system=auth.membership_type.value,
                    bungie_name=auth.bungie_name,
                    token=auth.token,
                    refresh_token=auth.refresh_token,
                    token_expiry=auth.token_expiry,
                    refresh_token_expiry=auth.refresh_token_expiry,
                    activities_last_updated=datetime_default,
                    collectibles_last_updated=datetime_default,
                    triumphs_last_updated=datetime_default,
                )

        return (
            BungieTokenOutput(
                bungie_name=user.bungie_name,
                user_should_set_up_cross_save=not auth.cross_save_setup,
                system=DestinySystemEnum(user.system).name,
            ),
            user,
            discord_id,
            guild_id,
        )

    async def update(self, db: AsyncSession, to_update: DiscordUsers, **update_kwargs) -> DiscordUsers:
        """Updates a profile"""

        async with update_lock:
            updated: DiscordUsers = await self._update(db=db, to_update=to_update, **update_kwargs)

            # update the cache in-place
            to_update.update_from_class(updated)

        return to_update

    async def invalidate_token(self, db: AsyncSession, user: DiscordUsers):
        """Invalidates a token by setting it to None"""

        await self.update(
            db=db,
            to_update=user,
            token=None,
        )

        try:
            # remove registration roles
            await self.remove_registration_roles(db=db, discord_id=user.discord_id)
        except CustomException:
            pass

    async def token_is_expired(self, user: DiscordUsers):
        """Checks if a token exists and the refresh token is not expired"""

        if not user.token:
            return True

        current_time = get_now_with_tz()
        if current_time > user.refresh_token_expiry:
            async with acquire_db_session() as db:
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
            self.cache.discord_users_by_destiny_id.pop(result.destiny_id)
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
                route="/roles",
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
                route="/roles",
                json={
                    "data": data,
                },
            )


discord_users = CRUDDiscordUser(DiscordUsers)
