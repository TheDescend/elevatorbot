import aiohttp
import aiohttp_client_cache

from datetime import timedelta

from networking.bungieAuth import handle_and_return_token
from networking.networkBackend import get_request, post_request
from networking.models import WebResponse
from static.config import BUNGIE_TOKEN



# base bungie headers
HEADERS = {
    'X-API-Key': BUNGIE_TOKEN,
    'Accept': 'application/json'
}

# the cache object. Low expire time since players dont want to wait an eternity for their stuff to update
cache = aiohttp_client_cache.SQLiteBackend(
    cache_name="networking/bungie_networking_cache",
    expire_after=timedelta(minutes=5),
)

# the base response if there is no token
no_token_response = WebResponse(
    content=None,
    status=None,
)
no_token_response.error = "NoToken"


async def get_json_from_url(url: str, headers: dict = None, params: dict = None, use_cache: bool = True) -> WebResponse:
    """
    Grabs JSON from the specified URL (no oauth)
    """

    # allows different urls than bungies to be called (fe. steam players)
    bungie_request = True
    if headers is None:
        headers = HEADERS
        bungie_request = False

    async with aiohttp_client_cache.CachedSession(cache=cache) as session:
        # use cache for the responses
        if use_cache:
            return await get_request(
                session=session,
                url=url,
                headers=headers,
                params=params,
                bungie_request=bungie_request
            )

        # do not use cache
        else:
            with session.disabled():
                return await get_request(
                    session=session,
                    url=url,
                    headers=headers,
                    params=params,
                    bungie_request=bungie_request
                )


async def get_json_from_bungie_with_token(url: str, discord_id: int, headers: dict = None, params: dict = None, use_cache: bool = True) -> WebResponse:
    """
    Takes url and discordID, returns dict with [token] = JSON
    """

    # get a working token or abort
    token = await handle_and_return_token(discord_id)
    if not token.token:
        no_token_response.error_message = token.error
        return no_token_response

    # use special token headers or the supplied ones
    if not headers:
        headers = HEADERS.copy().update({
            'Authorization': f'Bearer {token.token}',
        })

    # ignore cookies
    no_jar = aiohttp.DummyCookieJar()

    async with aiohttp_client_cache.CachedSession(cache=cache, cookie_jar=no_jar) as session:
        # use cache for the responses
        if use_cache:
            return await get_request(
                session=session,
                url=url,
                headers=headers,
                params=params,
                bungie_request=True
            )

        # do not use cache
        else:
            with session.disabled():
                return await get_request(
                    session=session,
                    url=url,
                    headers=headers,
                    params=params,
                    bungie_request=True
                )


async def post_json_to_url(url: str, data: dict, discord_id: int, headers: dict = None, params: dict = None) -> WebResponse:
    """
    Post info to bungie
    Parm discord_id must have the authentication for the action
    """

    # get a working token or abort
    token = await handle_and_return_token(discord_id)
    if not token.token:
        no_token_response.error_message = token.error
        return no_token_response

    # use special token headers or the supplied ones
    if not headers:
        headers = HEADERS.copy().update({
            'Authorization': f'Bearer {token.token}',
        })

    async with aiohttp_client_cache.CachedSession(cache=cache) as session:
        # do not use cache here
        with session.disabled():
            return await post_request(
                session=session,
                url=url,
                data=data,
                headers=headers,
                params=params,
                bungie_request=True
            )
