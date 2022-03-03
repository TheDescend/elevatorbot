import asyncio
import logging
import random
from typing import Callable, Coroutine, Optional
from urllib.parse import urlencode

import aiohttp
import aiohttp_client_cache
from aiohttp import ServerDisconnectedError
from orjson import orjson

from Backend.core.errors import CustomException
from Backend.networking.bungieRatelimiting import BungieRateLimiter
from Backend.networking.schemas import InternalWebResponse, WebResponse

# the limiter object which to not get rate-limited by bungie. One obj for ever instance!
bungie_limiter = BungieRateLimiter()
semaphore = asyncio.Semaphore(100)


class NetworkBase:
    bungie_request = True

    # get logger
    logger = logging.getLogger("bungieApi")
    logger_exceptions = logging.getLogger("bungieApiExceptions")

    # get limiter
    limiter = bungie_limiter

    # get semaphore
    semaphore = semaphore

    # how many times to retry a request
    max_web_request_tries = 10

    # callback to handle responses
    request_handler: Optional[Callable[..., Coroutine]] = None

    async def _request(
        self,
        session: aiohttp_client_cache.CachedSession | aiohttp.ClientSession,
        method: str,
        route: str,
        headers: dict = None,
        params: dict = None,
        json: dict = None,
        form_data: dict = None,
        _semaphored: bool = False,
    ) -> WebResponse:
        """Make a request to the url with the method and handles the result"""

        # respect the semaphore if it's a bungie request to not open 500 requests at once
        if self.bungie_request and not _semaphored:
            async with self.semaphore:
                return await self._request(
                    session=session,
                    method=method,
                    route=route,
                    headers=headers,
                    params=params,
                    json=json,
                    form_data=form_data,
                    _semaphored=True,
                )

        assert not (form_data and json), "Only json or form_data can be used"
        allow_redirects = False if self.bungie_request and method == "POST" else True

        # wait for a token from the rate limiter and use the semaphore
        if self.bungie_request:
            async with asyncio.Lock():
                await bungie_limiter.wait_for_token()

        # abort after max_web_request_tries tries
        for _ in range(self.max_web_request_tries):
            try:
                async with session.request(
                    method=method,
                    url=route,
                    headers=headers,
                    params=params,
                    json=json,
                    data=form_data,
                    allow_redirects=allow_redirects,
                ) as request:
                    if not self.request_handler:
                        self.request_handler = self.__handle_request_data

                    response = await self.request_handler(
                        request=request,
                        params=params,
                        route=route,
                    )

                    # try again
                    if response is None:
                        continue

                    # return response
                    else:
                        return WebResponse.from_dict(response.__dict__)

            except (asyncio.exceptions.TimeoutError, ConnectionResetError, ServerDisconnectedError) as error:
                self.logger.warning(
                    f"Retrying... - Timeout error ('{error}') for '{route}?{urlencode({} if params is None else params)}'"
                )
                await asyncio.sleep(random.randrange(2, 6))
                continue

        # return that it failed
        self.logger_exceptions.error(f"Request failed '{self.max_web_request_tries}' times, aborting for '{route}'")
        raise CustomException("UnknownError")

    async def __handle_request_data(
        self,
        request: aiohttp.ClientResponse | aiohttp_client_cache.CachedResponse,
        route: str,
        params: Optional[dict],
    ) -> Optional[InternalWebResponse]:
        """Handle the request results"""

        if not params:
            params = {}
        route_with_params = f"{route}?{urlencode(params)}"

        # catch the content type "application/octet-stream" which is returned for some routes
        if "application/octet-stream" in request.headers["Content-Type"]:
            pass

        # make sure the return is a json, sometimes we get a http file for some reason
        elif "application/json" not in request.headers["Content-Type"]:
            self.logger_exceptions.error(
                f"""'{request.status}': Retrying... - Wrong content type '{request.headers["Content-Type"]}' with reason '{request.reason}' for '{route_with_params}'"""
            )
            print(f"""Bungie returned Content-Type: {request.headers["Content-Type"]}""")
            if request.status == 200:
                self.logger_exceptions.error(f"Wrong content type returned text: '{await request.text()}'")
            await asyncio.sleep(3)
            return

        # get the response as a json
        try:
            response = InternalWebResponse(
                content=await request.json(loads=orjson.loads),
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
            self.logger_exceptions.error(f"'{request.status}': Payload error, retrying for '{route_with_params}'")
            return
        except aiohttp.ContentTypeError:
            response = InternalWebResponse(
                status=request.status,
            )

        # if response is ok return it
        if response.status == 200:
            response.success = True

            # remove the leading "Response" from the request (if exists)
            if "Response" in response.content:
                response.content = response.content["Response"]

            return response

        # handling any errors if not ok
        await self.__handle_bungie_errors(
            route=route, params=params, response=response, route_with_params=route_with_params
        )

    async def __handle_bungie_errors(
        self, route: str, params: dict, response: InternalWebResponse, route_with_params: str
    ):
        """Looks for typical bungie errors and handles / logs them"""

        match (response.status, response.error):
            case (_, "SystemDisabled"):
                raise CustomException("BungieDed")

            case (401, _) | (_, "invalid_grant" | "AuthorizationCodeInvalid"):
                # unauthorized
                self.logger_exceptions.warning(
                    f"'{response.status} - {response.error}': Unauthorized (too slow, user fault) request for '{route_with_params}'"
                )
                raise CustomException("BungieUnauthorized")

            case (status, "PerEndpointRequestThrottleExceeded" | "DestinyDirectBabelClientTimeout"):
                # we are getting throttled (should never be called in theory)
                self.logger.warning(
                    f"'{status} - {response.error}': Retrying... - Getting throttled for '{route_with_params}' - '{response}'"
                )

                throttle_seconds = response.content["ThrottleSeconds"]

                # reset the ratelimit giver
                self.limiter.tokens = 0
                await asyncio.sleep(throttle_seconds)

            case (status, "ClanInviteAlreadyMember"):
                # if user is in clan
                raise CustomException("BungieClanInviteAlreadyMember")

            case (status, "GroupMembershipNotFound"):
                # if user isn't in clan
                raise CustomException("BungieGroupMembershipNotFound")

            case (status, "DestinyItemNotFound"):
                # if user doesn't have that item
                raise CustomException("BungieDestinyItemNotFound")

            case (status, "DestinyPrivacyRestriction"):
                # private profile
                raise CustomException("BungieDestinyPrivacyRestriction")

            case (status, "DestinyDirectBabelClientTimeout"):
                # timeout
                self.logger.warning(
                    f"'{status} - {response.error}': Retrying... - Getting timeouts for '{route_with_params}' - '{response}'"
                )
                await asyncio.sleep(60)

            case (status, "DestinyServiceFailure"):
                # timeout
                self.logger.warning(
                    f"'{status} - {response.error}': Retrying... - Bungie is having problems '{route_with_params}' - '{response}'"
                )
                await asyncio.sleep(60)

            case (status, "ClanTargetDisallowsInvites"):
                # user has disallowed clan invites
                raise CustomException("BungieClanTargetDisallowsInvites")

            case (status, "AuthorizationRecordRevoked" | "AuthorizationRecordExpired"):
                # users tokens are no longer valid
                raise CustomException("NoToken")

            case (404, error):
                # not found
                self.logger_exceptions.error(
                    f"'{response.status} - {error}': No stats found for '{route_with_params}' - '{response}'"
                )
                raise CustomException("BungieBadRequest")

            case (429, error):
                # rate limited
                self.logger.warning(
                    f"'{response.status} - {error}': Retrying... - Getting rate limited for '{route_with_params}' - '{response}'"
                )
                await asyncio.sleep(2)

            case (400, error):
                # generic bad request, such as wrong format
                self.logger_exceptions.error(
                    f"'{response.status} - {error}': Generic bad request for '{route_with_params}' - '{response}'"
                )
                raise CustomException("BungieBadRequest")

            case (503, error):
                self.logger.warning(
                    f"'{response.status} - {error}': Retrying... - Server is overloaded for '{route_with_params}' - '{response}'"
                )
                await asyncio.sleep(10)

            case (status, error):
                # catch the rest
                self.logger_exceptions.error(
                    f"'{status} - {error}': Retrying... - Request failed for '{route_with_params}' - '{response}'"
                )
                await asyncio.sleep(2)

        return False
