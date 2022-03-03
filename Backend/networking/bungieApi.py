import os
from datetime import timedelta
from typing import Optional

import aiohttp
import aiohttp_client_cache
import orjson
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud import discord_users
from Backend.database.base import get_async_sessionmaker
from Backend.database.models import DiscordUsers
from Backend.networking.base import NetworkBase
from Backend.networking.bungieAuth import BungieAuth
from Backend.networking.bungieRoutes import manifest_route, pgcr_route
from Backend.networking.schemas import WebResponse

# the cache object
# low expire time since players don't want to wait an eternity for their stuff to update
from Shared.functions.readSettingsFile import get_setting

bungie_cache = aiohttp_client_cache.RedisBackend(
    cache_name="backend",
    address=f"""redis://{os.environ.get("REDIS_HOST")}:{os.environ.get("REDIS_PORT")}""",
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
headers = {"X-API-Key": get_setting("BUNGIE_APPLICATION_API_KEY"), "Accept": "application/json"}


class BungieApi(NetworkBase):
    """Handles all networking to any API. To call an api that is not bungies, change the headers"""

    # base bungie headers
    normal_headers = headers.copy()
    auth_headers = headers.copy()

    # redis cache
    cache = bungie_cache

    def __init__(
        self,
        db: AsyncSession,
        user: Optional[DiscordUsers] = None,
        headers: Optional[dict] = None,
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

    async def get(
        self, route: str, params: dict = None, use_cache: bool = True, with_token: bool = False
    ) -> WebResponse:
        """Grabs JSON from the specified URL (no oauth)"""

        no_jar = None

        # check if we need a token
        if not with_token:
            # don't need user auth for some endpoints
            if not any([ok_route in route for ok_route in [pgcr_route, manifest_route]]):
                # check if the user has a private profile, if so we use oauth
                if self.user:
                    if self.user.private_profile:
                        # then we use a token
                        with_token = True

        # use a token if we need to
        if with_token:
            await self.__set_auth_headers()

            # ignore cookies
            no_jar = aiohttp.DummyCookieJar()

        try:
            async with aiohttp_client_cache.CachedSession(
                cache=self.cache, json_serialize=lambda x: orjson.dumps(x).decode(), cookie_jar=no_jar
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
                self.user = await discord_users.update(db=self.db, to_update=self.user, private_profile=True)

                # then call the same endpoint again, this time with a token
                return await self.get(route=route, params=params, use_cache=use_cache, with_token=True)

            else:
                # otherwise, raise error again
                raise exc

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
