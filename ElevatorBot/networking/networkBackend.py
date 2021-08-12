import asyncio
import logging
import random
from typing import Optional, Union

import aiohttp
import aiohttp_client_cache

from ElevatorBot.networking.bungieRatelimiting import BungieRateLimiter
from ElevatorBot.networking.models import WebResponse


# get logger
logger = logging.getLogger('network')

# the limiter object which to not get rate-limited by bungie
bungie_limiter = BungieRateLimiter()

# how many times to retry a request
max_web_request_tries = 10


async def get_request(
    session: Union[aiohttp_client_cache.CachedSession, aiohttp.ClientSession],
    url: str,
    headers: dict = None,
    params: dict = None,
    bungie_request: bool = True
) -> WebResponse:
    """
    Makes a get request to the specified url
    Returns instance of WebResponse()
    """

    response = None

    # wait for a token from the rate limiter
    if bungie_request:
        async with asyncio.Lock():
            await bungie_limiter.wait_for_token()

    # abort after max_web_request_tries tries
    for _ in range(max_web_request_tries):
        try:
            async with session.get(
                url=url,
                headers=headers,
                params=params,
            ) as request:
                response = await handle_request_data(
                    request=request,
                    url=url,
                )

                # try again
                if response is None:
                    continue

                # return response
                else:
                    return response

        except (asyncio.exceptions.TimeoutError, ConnectionResetError):
            logger.error("Timeout error for '%s'", url)
            await asyncio.sleep(random.randrange(2, 6))
            continue

    # return that it failed
    if response:
        return response
    logger.error("Request failed '%s' times, aborting for '%s'", max_web_request_tries, url)
    no_response = WebResponse(
        content=None,
        status=None,
    )
    no_response.error_message = "Request failed"
    return no_response


async def post_request(
    session: Union[aiohttp_client_cache.CachedSession, aiohttp.ClientSession],
    url: str,
    data: dict,
    headers: dict = None,
    params: dict = None,
    bungie_request: bool = True
) -> WebResponse:
    """
    Makes a post request to the specified url
    Returns instance of WebResponse()
    """

    response = None

    # wait for a token from the rate limiter
    if bungie_request:
        async with asyncio.Lock():
            await bungie_limiter.wait_for_token()

    # abort after max_web_request_tries tries
    for _ in range(max_web_request_tries):
        try:
            async with session.post(
                url=url,
                data=data,
                headers=headers,
                params=params,
                allow_redirects=False,
            ) as request:
                response = await handle_request_data(
                    request=request,
                    url=url,
                )

                # try again
                if response is None:
                    continue

                # return response
                else:
                    return response

        except (asyncio.exceptions.TimeoutError, ConnectionResetError):
            logger.error("Timeout error for '%s'", url)
            await asyncio.sleep(random.randrange(2, 6))
            continue

    # return that it failed
    if response:
        return response
    logger.error("Request failed '%s' times, aborting for '%s'", max_web_request_tries, url)
    no_response = WebResponse(
        content=None,
        status=None,
    )
    no_response.error_message = "Request failed"
    return no_response


async def handle_request_data(
    request: Union[aiohttp.ClientResponse, aiohttp_client_cache.CachedResponse],
    url: str
) -> Optional[WebResponse]:
    """
    Handle the request results
    """

    # make sure the return is a json, sometimes we get a http file for some reason
    if 'application/json' not in request.headers['Content-Type']:
        logger.error("'%s': Wrong content type '%s' with reason '%s' for '%s'", request.status, request.headers["Content-Type"], request.reason, url)
        if request.status == 200:
            logger.error("Wrong content type returned text: '%s'", await request.text())
        await asyncio.sleep(3)
        return

    # get the response as a json
    try:
        response = WebResponse(
            content=await request.json(),
            status=request.status,
        )

        # set the error vars
        response.error = None
        if "ErrorStatus" in response.content:
            response.error = response.content["ErrorStatus"]
        elif "error_description" in response.content:
            response.error = response.content["error_description"]
        response.error_code = response.content["ErrorCode"] if "ErrorCode" in response.content else None
        response.error_message = response.content["Message"] if "Message" in response.content else None

        # set if the response was cached
        try:
            response.from_cache = request.from_cache
        except AttributeError:
            response.from_cache = False

    except aiohttp.ClientPayloadError:
        logger.error("'%s': Payload error, retrying for '%s'", request.status, url)
        return
    except aiohttp.ContentTypeError:
        logger.error("'%s': Content type error, retrying for '%s'", request.status, url)
        return

    # if response is ok return it
    if response.status == 200:
        response.success = True
        return response

    # handling any errors if not ok
    stop_loop_due_to_error = await handle_bungie_errors(
        url=url,
        response=response,
    )
    if stop_loop_due_to_error:
        return response


async def handle_bungie_errors(
    url: str,
    response: WebResponse
) -> bool:
    """
    Looks for typical bungie errors and handles / logs them
    Returns: if_loop_should_be_stopped: bool
    """

    # generic bad request, such as wrong format
    if response.status == 400:
        logger.error("'%s - %s': Generic bad request for '%s' - '%s'", response.status, response.error, url, response.error_message)
        return True

    # not found
    elif response.status == 404:
        logger.error("'%s - %s': No stats found for '%s' - '%s'", response.status, response.error, url, response.error_message)
        return True

    # bungie is ded
    elif response.status == 503:
        logger.error("'%s - %s': Server is overloaded for '%s' - '%s'", response.status, response.error, url, response.error_message)
        await asyncio.sleep(10)

    # rate limited
    elif response.status == 429:
        logger.warning("'%s - %s': Getting rate limited for '%s' - '%s'", response.status, response.error, url, response.error_message)
        await asyncio.sleep(2)

    # we we are getting throttled
    elif response.error == "PerEndpointRequestThrottleExceeded" or response.error == "DestinyDirectBabelClientTimeout":
        throttle_seconds = response.content['ErrorStatus']["ThrottleSeconds"]

        logger.warning(
            "'%s - %s': Getting throttled, waiting '%s' for '%s' - '%s'", response.status, response.error, throttle_seconds or 'for Babel', url,
            response.error_message
        )
        await asyncio.sleep(throttle_seconds + random.randrange(1, 3))

    # if user doesn't have that item
    elif response.error == "DestinyItemNotFound":
        logger.error("'%s - %s': User doesn't have that item for '%s' - '%s'", response.status, response.error, url, response.error_message)
        return True

    # private profile
    elif response.error == "DestinyPrivacyRestriction":
        logger.error("'%s - %s': User has private Profile for '%s' - '%s'", response.status, response.error, url, response.error_message)
        return True

    # timeout
    elif response.error == "DestinyDirectBabelClientTimeout":
        logger.warning("'%s - %s': Getting timeouts for '%s' - '%s'", response.status, response.error, url, response.error_message)
        await asyncio.sleep(60)

    # user has disallowed clan invites
    elif response.error == "ClanTargetDisallowsInvites":
        logger.error("'%s - %s': User disallows clan invites '%s' - '%s'", response.status, response.error, url, response.error_message)
        return True

    # user has disallowed clan invites
    elif response.error == "AuthorizationRecordRevoked":
        logger.error(
            "'%s - %s': User refresh token is outdated and they need to re-register for '%s' - '%s'", response.status, response.error, url,
            response.error_message
        )
        return True

    else:
        logger.error("'%s - %s': Request failed for '%s' - '%s'", response.status, response.error, url, response.error_message)
        await asyncio.sleep(2)

    return False
