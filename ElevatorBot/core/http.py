import dataclasses
import logging
from typing import Optional

import aiohttp
import discord
from aiohttp import ClientSession, ClientTimeout

from ElevatorBot.core.results import BackendResult


@dataclasses.dataclass
class BaseBackendConnection:
    """
    Define default backend functions such as get get, post and _delete.
    These can be called by subclasses, and automatically handle networking and error handling
    """

    # save discord information
    client: discord.Client

    # get logger
    logger: logging.Logger = dataclasses.field(
        default=logging.getLogger("backendNetworking"),
        init=False,
        compare=False,
        repr=False,
    )

    # get aiohttp session
    backend_session: ClientSession = dataclasses.field(
        default=aiohttp.ClientSession(
            timeout=ClientTimeout(
                # give request a max timeout of half an hour
                total=30
                * 60
            )
        ),
        init=False,
        compare=False,
        repr=False,
    )

    def __bool__(self):
        """Bool function to test if this exist. Useful for testing if this class got returned and not BackendResult, can be returned on errors"""

        return True

    async def _backend_get(self, route: str, params: dict = None) -> BackendResult:
        """Make a get request to the specified backend route and return the results"""

        async with self.backend_session as session:
            async with session.get(
                url=route,
                params=params,
            ) as response:
                return self.__backend_parse_response(response)

    async def _backend_post(self, route: str, data: dict = None, params: dict = None) -> BackendResult:
        """Make a post request to the specified backend route and return the results"""

        async with self.backend_session as session:
            async with session.post(
                url=route,
                params=params,
                data=data,
            ) as response:
                return self.__backend_parse_response(response)

    async def _backend_delete(self, route: str, params: dict = None) -> BackendResult:
        """Make a _delete request to the specified backend route and return the results"""

        async with self.backend_session as session:
            async with session.delete(
                url=route,
                params=params,
            ) as response:
                return self.__backend_parse_response(response)

    def __backend_parse_response(self, response: aiohttp.ClientResponse) -> BackendResult:
        """Handle any errors and then return the content of the response"""

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
            result.update(
                {
                    "error": self.__backend_handle_errors(response),
                }
            )

        result.update(
            {
                "success": success,
            }
        )

        return BackendResult(**result)

    def __backend_handle_errors(self, response: aiohttp.ClientResponse) -> Optional[str]:
        """Handles potential errors. Returns None, None if the error should not be returned to the user and str, str if something should be returned to the user"""

        if response.status == 409:
            # this means the errors isn't really an error and we want to return info to the user
            self.logger.info("%s: '%s' - '%s'", response.status, response.method, response.url)
            error_json = await response.json()
            return error_json["error"]

        else:
            # if we dont know anything, just log it with the error
            self.logger.error(
                "%s: '%s' - '%s' - '%s'",
                response.status,
                response.method,
                response.url,
                await response.json(),
            )
            return None
