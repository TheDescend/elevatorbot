import asyncio
import logging
import random
from typing import Optional, Union

import aiohttp
import aiohttp_client_cache

from Backend.core.errors import CustomException
from Backend.networking.bungieRatelimiting import BungieRateLimiter
from Backend.networking.schemas import InternalWebResponse, WebResponse


# the limiter object which to not get rate-limited by bungie. One obj for ever instance!
bungie_limiter = BungieRateLimiter()


class NetworkBase:
    bungie_request = True

    # get logger
    logger = logging.getLogger("bungieApi")

    # get limiter
    limiter = bungie_limiter

    # how many times to retry a request
    max_web_request_tries = 10

    async def _get_request(
        self,
        session: Union[aiohttp_client_cache.CachedSession, aiohttp.ClientSession],
        route: str,
        headers: dict = None,
        params: dict = None,
    ) -> WebResponse:
        """
        Makes a get request to the specified url
        Returns instance of WebResponse()
        """

        # wait for a token from the rate limiter
        if self.bungie_request:
            async with asyncio.Lock():
                await bungie_limiter.wait_for_token()

        # abort after max_web_request_tries tries
        for _ in range(self.max_web_request_tries):
            try:
                async with session.get(
                    url=route,
                    headers=headers,
                    params=params,
                ) as request:
                    response = await self.__handle_request_data(
                        request=request,
                        route=route,
                    )

                    # try again
                    if response is None:
                        continue

                    # return response
                    else:
                        return WebResponse(**response.__dict__)

            except (asyncio.exceptions.TimeoutError, ConnectionResetError):
                self.logger.error("Timeout error for '%s'", route)
                await asyncio.sleep(random.randrange(2, 6))
                continue

        # return that it failed
        self.logger.error(
            "Request failed '%s' times, aborting for '%s'", self.max_web_request_tries, route
        )
        raise CustomException("UnknownError")


    async def _post_request(
        self,
        session: Union[aiohttp_client_cache.CachedSession, aiohttp.ClientSession],
        route: str,
        data: dict,
        headers: dict = None,
        params: dict = None,
    ) -> WebResponse:
        """
        Makes a post request to the specified url
        Returns instance of WebResponse()
        """

        # wait for a token from the rate limiter
        if self.bungie_request:
            async with asyncio.Lock():
                await bungie_limiter.wait_for_token()

        # abort after max_web_request_tries tries
        for _ in range(self.max_web_request_tries):
            try:
                async with session.post(
                    url=route,
                    data=data,
                    headers=headers,
                    params=params,
                    allow_redirects=False,
                ) as request:
                    response = await self.__handle_request_data(
                        request=request,
                        route=route,
                    )

                    # try again
                    if response is None:
                        continue

                    # return response
                    else:
                        return WebResponse(**response.__dict__)

            except (asyncio.exceptions.TimeoutError, ConnectionResetError):
                self.logger.error("Timeout error for '%s'", route)
                await asyncio.sleep(random.randrange(2, 6))
                continue

        # return that it failed
        self.logger.error(
            "Request failed '%s' times, aborting for '%s'", self.max_web_request_tries, route
        )
        raise CustomException("UnknownError")


    async def __handle_request_data(
        self,
        request: Union[aiohttp.ClientResponse, aiohttp_client_cache.CachedResponse],
        route: str,
    ) -> Optional[InternalWebResponse]:
        """ Handle the request results """

        # make sure the return is a json, sometimes we get a http file for some reason
        if "application/json" not in request.headers["Content-Type"]:
            self.logger.error(
                "'%s': Wrong content type '%s' with reason '%s' for '%s'",
                request.status,
                request.headers["Content-Type"],
                request.reason,
                route,
            )
            if request.status == 200:
                self.logger.error("Wrong content type returned text: '%s'", await request.text())
            await asyncio.sleep(3)
            return

        # get the response as a json
        try:
            response = InternalWebResponse(
                content=await request.json(),
                status=request.status,
            )

            # set the error vars
            response.error = None
            if "ErrorStatus" in response.content:
                response.error = response.content["ErrorStatus"]
            elif "error_description" in response.content:
                response.error = response.content["error_description"]
            response.error_code = (
                response.content["ErrorCode"] if "ErrorCode" in response.content else None
            )
            response.error_message = (
                response.content["Message"] if "Message" in response.content else None
            )

            # set if the response was cached
            try:
                response.from_cache = request.from_cache
            except AttributeError:
                response.from_cache = False

        except aiohttp.ClientPayloadError:
            self.logger.error("'%s': Payload error, retrying for '%s'", request.status, route)
            return
        except aiohttp.ContentTypeError:
            self.logger.error("'%s': Content type error, retrying for '%s'", request.status, route)
            return

        # if response is ok return it
        if response.status == 200:
            response.success = True

            # remove the leading "Reponse" from the request (if exists)
            if "Response" in response.content:
                response.content = response.content["Response"]

            return response

        # handling any errors if not ok
        await self.__handle_bungie_errors(
            route=route,
            response=response,
        )


    async def __handle_bungie_errors(
        self,
        route: str,
        response: InternalWebResponse
    ):
        """ Looks for typical bungie errors and handles / logs them """

        # generic bad request, such as wrong format
        if response.status == 400:
            self.logger.error(
                "'%s - %s': Generic bad request for '%s' - '%s'",
                response.status,
                response.error,
                route,
                response,
            )
            raise CustomException("BungieDed")

        # not found
        elif response.status == 404:
            self.logger.error(
                "'%s - %s': No stats found for '%s' - '%s'",
                response.status,
                response.error,
                route,
                response,
            )
            raise CustomException("BungieBadRequest")

        # bungie is ded
        elif response.status == 503:
            self.logger.error(
                "'%s - %s': Server is overloaded for '%s' - '%s'",
                response.status,
                response.error,
                route,
                response,
            )
            await asyncio.sleep(10)

        # rate limited
        elif response.status == 429:
            self.logger.warning(
                "'%s - %s': Getting rate limited for '%s' - '%s'",
                response.status,
                response.error,
                route,
                response,
            )
            await asyncio.sleep(2)

        # we we are getting throttled
        elif (
            response.error == "PerEndpointRequestThrottleExceeded"
            or response.error == "DestinyDirectBabelClientTimeout"
        ):
            self.logger.warning(
                "'%s - %s': Getting throttled for '%s' - '%s'",
                response.status,
                response.error,
                route,
                response,
            )

            throttle_seconds = response.content["ErrorStatus"]["ThrottleSeconds"]

            await asyncio.sleep(throttle_seconds + random.randrange(1, 3))

        # if user doesn't have that item
        elif response.error == "DestinyItemNotFound":
            self.logger.error(
                "'%s - %s': User doesn't have that item for '%s' - '%s'",
                response.status,
                response.error,
                route,
                response,
            )
            raise CustomException("BungieDestinyItemNotFound")

        # private profile
        elif response.error == "DestinyPrivacyRestriction":
            self.logger.error(
                "'%s - %s': User has private Profile for '%s' - '%s'",
                response.status,
                response.error,
                route,
                response,
            )
            raise CustomException("BungieDestinyPrivacyRestriction")

        # timeout
        elif response.error == "DestinyDirectBabelClientTimeout":
            self.logger.warning(
                "'%s - %s': Getting timeouts for '%s' - '%s'",
                response.status,
                response.error,
                route,
                response,
            )
            await asyncio.sleep(60)

        # user has disallowed clan invites
        elif response.error == "ClanTargetDisallowsInvites":
            self.logger.error(
                "'%s - %s': User disallows clan invites '%s' - '%s'",
                response.status,
                response.error,
                route,
                response,
            )
            raise CustomException("BungieClanTargetDisallowsInvites")

        # user has disallowed clan invites
        elif response.error == "AuthorizationRecordRevoked":
            self.logger.error(
                "'%s - %s': User refresh token is outdated and they need to re-register for '%s' - '%s'",
                response.status,
                response,
                route,
                response.error_message,
            )
            raise CustomException("NoToken")

        else:
            self.logger.error(
                "'%s - %s': Request failed for '%s' - '%s'",
                response.status,
                response.error,
                route,
                response,
            )
            await asyncio.sleep(2)

        return False
