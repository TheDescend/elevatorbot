from datetime import timedelta

import aiohttp
import aiohttp_client_cache
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.networking.bungieAuth import BungieAuth
from Backend.networking.schemas import WebResponse
from Backend.networking.base import NetworkBase
from settings import BUNGIE_TOKEN



class BungieApi(NetworkBase):
    """ Handles all networking to any API. To call an api that is not bungies, change the headers """

    # base bungie headers
    normal_headers = {
        "X-API-Key": BUNGIE_TOKEN,
        "Accept": "application/json"
    }
    auth_headers = normal_headers.copy()

    # the cache object. Low expire time since players dont want to wait an eternity for their stuff to _update
    cache = aiohttp_client_cache.SQLiteBackend(
        cache_name="networking/bungie_networking_cache",
        expire_after=timedelta(minutes=5),
    )


    def __init__(
        self,
        discord_id: int,
        headers: dict = None
    ):
        self.discord_id = discord_id

        # allows different urls than bungies to be called (fe. steam players)
        if headers:
            self.normal_headers = headers
            self.auth_headers = headers
            self.bungie_request = False


    async def get_json_from_url(
        self,
        route: str,
        params: dict = None,
        use_cache: bool = True
    ) -> WebResponse:
        """ Grabs JSON from the specified URL (no oauth) """

        async with aiohttp_client_cache.CachedSession(cache=self.cache) as session:
            # use cache for the responses
            if use_cache:
                return await self._get_request(
                    session=session,
                    route=route,
                    headers=self.normal_headers,
                    params=params,
                )

            # do not use cache
            else:
                async with session.disabled():
                    return await self._get_request(
                        session=session,
                        route=route,
                        headers=self.normal_headers,
                        params=params,
                    )


    async def get_json_from_bungie_with_token(
        self,
        db: AsyncSession,
        route: str,
        params: dict = None,
        use_cache: bool = True,
    ) -> WebResponse:
        """ Grabs JSON from the specified URL (oauth) """

        # set the auth headers to a working token
        await self.__set_auth_headers(db)

        # ignore cookies
        no_jar = aiohttp.DummyCookieJar()

        async with aiohttp_client_cache.CachedSession(
            cache=self.cache,
            cookie_jar=no_jar
        ) as session:
            # use cache for the responses
            if use_cache:
                return await self._get_request(
                    session=session,
                    route=route,
                    headers=self.auth_headers,
                    params=params,
                )

            # do not use cache
            else:
                async with session.disabled():
                    return await self._get_request(
                        session=session,
                        route=route,
                        headers=self.auth_headers,
                        params=params,
                    )


    async def post_json_to_url(
        self,
        db: AsyncSession,
        route: str,
        data: dict,
        params: dict = None
    ) -> WebResponse:
        """ Post data to bungie. self.discord_id must have the authentication for the action """

        # set the auth headers to a working token
        await self.__set_auth_headers(db)

        async with aiohttp_client_cache.CachedSession(cache=self.cache) as session:
            # do not use cache here
            async with session.disabled():
                return await self._post_request(
                    session=session,
                    route=route,
                    data=data,
                    headers=self.auth_headers,
                    params=params,
                )

    async def __set_auth_headers(self, db: AsyncSession):
        """ Update the auth headers to include a working token. Raise an error if that doesnt exist """

        # get a working token or abort
        auth = BungieAuth(
            discord_id=self.discord_id,
            db=db
        )
        token = await auth.get_working_token()

        # use special token headers if its a bungie request
        if self.bungie_request:
            self.auth_headers = self.auth_headers.update(
                {
                    "Authorization": f"Bearer {token}",
                }
            )
