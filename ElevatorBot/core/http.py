import dataclasses
import logging
from typing import Optional, Tuple

import aiohttp
import discord
from aiohttp import ClientTimeout


@dataclasses.dataclass
class BackendResult:
    """ Holds the return info """

    success: bool
    result: Optional[dict]
    error: Optional[str]
    error_message: Optional[str]


class BaseBackendConnection:
    """
    Define default backend functions such as get get, post and delete.
    These can be called by subclasses, and automatically handle networking and error handling
    """


    def __init__(
        self,
        discord_member: discord.Member,
        discord_guild: discord.Guild,
        discord_channel: discord.GroupChannel
    ):
        # save discord information
        self.discord_member = discord_member
        self.discord_guild = discord_guild
        self.discord_channel = discord_channel

        # get logger
        self.logger = logging.getLogger("backendNetworking")

        # get aiohttp session
        self.backend_session = aiohttp.ClientSession(
            timeout=ClientTimeout(
                # give request a max timeout of half an hour
                total=30 * 60
            )
        )


    async def backend_get(
        self,
        route: str,
        params: dict = None
    ) -> BackendResult:
        """ Make a get request to the specified backend route and return the results """

        async with self.backend_session as session:
            async with session.get(
                url=route,
                params=params,
            ) as response:
                return self.__parse_response(response)


    async def backend_post(
        self,
        route: str,
        data: dict,
        params: dict = None
    ) -> BackendResult:
        """ Make a post request to the specified backend route and return the results """

        async with self.backend_session as session:
            async with session.post(
                url=route,
                params=params,
                data=data,
            ) as response:
                return self.__parse_response(response)


    async def backend_delete(
        self,
        route: str,
        params: dict = None
    ) -> BackendResult:
        """ Make a delete request to the specified backend route and return the results """

        async with self.backend_session as session:
            async with session.delete(
                url=route,
                params=params,
            ) as response:
                return self.__parse_response(response)


    def __parse_response(
        self,
        response: aiohttp.ClientResponse
    ) -> BackendResult:
        """ Handle any errors and then return the content of the response """

        result = {}
        if response.status == 200:
            success = True
            self.logger.info("%s: '%s' - '%s'", response.status, response.method, response.url)
            result.update(
                {
                    "result": await response.json(),
                }
            )

        else:
            success = False
            error, error_message = self.__backend_handle_errors(response)
            result.update(
                {
                    "error": error,
                    "error_message": error_message,
                }
            )

        result.update(
            {
                "success": success,
            }
        )

        return BackendResult(**result)


    def __backend_handle_errors(
        self,
        response: aiohttp.ClientResponse
    ) -> Tuple[Optional[str], Optional[str]]:
        """ Handles potential errors. Returns None, None if the error should not be returned to the user and str, str if something should be returned to the user """

        if response.status == 409:
            # this means the errors isn't really an error and we want to return info to the user
            self.logger.info("%s: '%s' - '%s'", response.status, response.method, response.url)
            error_json = await response.json()
            return error_json["error"], error_json["error_message"]

        else:
            # if we dont know anything, just log it with the error
            self.logger.error("%s: '%s' - '%s' - '%s'", response.status, response.method, response.url, await response.json())
            return None, None
