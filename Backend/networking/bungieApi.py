from datetime import timedelta

import aiohttp
import aiohttp_client_cache
import orjson
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud import discord_users
from Backend.database.models import DiscordUsers
from Backend.networking.base import NetworkBase
from Backend.networking.bungieAuth import BungieAuth
from Backend.networking.schemas import WebResponse
from settings import BUNGIE_TOKEN


class BungieApi(NetworkBase):
    """Handles all networking to any API. To call an api that is not bungies, change the headers"""

    # base bungie headers
    normal_headers = {"X-API-Key": BUNGIE_TOKEN, "Accept": "application/json"}
    auth_headers = normal_headers.copy()

    # the cache object. Low expire time since players don't want to wait an eternity for their stuff to update
    cache = aiohttp_client_cache.SQLiteBackend(
        cache_name="networking/bungie_networking_cache",
        allowed_methods=["GET"],
        expire_after=timedelta(minutes=5),
        urls_expire_after={
            "**/platform/app/oauth/token": 0,  # do not save token stuff
            "**/Destiny2/Stats/PostGameCarnageReport": 0,  # do not save pgcr. We save them anyway and don't look them up more than once
            "**/Destiny2/*/Profile/**components=": timedelta(minutes=30),  # profile call
            "**/Destiny2/*/Account/*/Stats": timedelta(minutes=60),  # stats
            "**/Destiny2/*/Account/*/Character/*/Stats/Activities": timedelta(minutes=5),  # activity history
            "**/GroupV2/*/Members": timedelta(minutes=60),  # all clan member stuff
            "**/GroupV2/*/AdminsAndFounder": timedelta(minutes=60),  # all clan admin stuff
            "**/GroupV2": timedelta(days=1),  # all clan stuff
        },
    )

    def __init__(
        self,
        db: AsyncSession,
        user: DiscordUsers = None,
        headers: dict = None,
        i_understand_what_im_doing_and_that_setting_this_to_true_might_break_stuff: bool = False,
    ):

        assert (
            user or headers or i_understand_what_im_doing_and_that_setting_this_to_true_might_break_stuff
        ), "One argument needs to be defined"
        self.user = user
        self.discord_id = user.discord_id if user else None
        self.db = db

        # allows different urls than bungies to be called (fe. steam players)
        if headers:
            self.normal_headers = headers
            self.auth_headers = headers
            self.bungie_request = False

    async def get(self, route: str, params: dict = None, use_cache: bool = True) -> WebResponse:
        """Grabs JSON from the specified URL (no oauth)"""

        # check if the user has a private profile, if so we use oauth
        if self.user:
            if self.user.private_profile:
                # then we use get_with_token()
                return await self.get_with_token(route=route, params=params, use_cache=use_cache)

        try:
            async with aiohttp_client_cache.CachedSession(
                cache=self.cache, json_serialize=lambda x: orjson.dumps(x).decode()
            ) as session:
                # use cache for the responses
                if use_cache:
                    return await self._request(
                        session=session,
                        method="GET",
                        route=route,
                        headers=self.normal_headers,
                        params=params,
                    )

                # do not use cache
                else:
                    async with session.disabled():
                        return await self._request(
                            session=session,
                            method="GET",
                            route=route,
                            headers=self.normal_headers,
                            params=params,
                        )

        except CustomException as exc:
            if exc.error == "BungieDestinyPrivacyRestriction":
                # catch the BungieDestinyPrivacyRestriction error to change privacy settings in our db
                await discord_users.update(db=self.db, to_update=self.user, has_private_profile=True)

                # then call the same endpoint again, this time with a token
                return await self.get_with_token(route=route, params=params, use_cache=use_cache)

            else:
                # otherwise raise error again
                raise exc

    async def get_with_token(self, route: str, params: dict = None, use_cache: bool = True) -> WebResponse:
        """Grabs JSON from the specified URL (oauth)"""

        # set the auth headers to a working token
        await self.__set_auth_headers()

        # ignore cookies
        no_jar = aiohttp.DummyCookieJar()

        async with aiohttp_client_cache.CachedSession(cache=self.cache, cookie_jar=no_jar) as session:
            # use cache for the responses
            if use_cache:
                return await self._request(
                    session=session,
                    method="GET",
                    route=route,
                    headers=self.auth_headers,
                    params=params,
                )

            # do not use cache
            else:
                async with session.disabled():
                    return await self._request(
                        session=session,
                        method="GET",
                        route=route,
                        headers=self.auth_headers,
                        params=params,
                    )

    async def post(self, route: str, json: dict = None, params: dict = None) -> WebResponse:
        """Post data to bungie. self.discord_id must have the authentication for the action"""

        # set the auth headers to a working token
        await self.__set_auth_headers()

        async with aiohttp_client_cache.CachedSession(cache=self.cache) as session:
            # do not use cache here
            async with session.disabled():
                return await self._request(
                    session=session,
                    method="POST",
                    route=route,
                    json=json,
                    headers=self.auth_headers,
                    params=params,
                )

    async def __set_auth_headers(self):
        """Update the auth headers to include a working token. Raise an error if that doesnt exist"""

        # get a working token or abort
        auth = BungieAuth(db=self.db, user=self.user)
        token = await auth.get_working_token()

        # use special token headers if its a bungie request
        if self.bungie_request:
            self.auth_headers.update(
                {
                    "Authorization": f"Bearer {token}",
                }
            )
