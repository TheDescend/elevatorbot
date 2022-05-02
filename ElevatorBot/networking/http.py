import asyncio
import dataclasses
import logging
import os
from asyncio import Semaphore
from datetime import timedelta
from typing import Optional

import aiohttp
import aiohttp_client_cache
import orjson
from aiohttp import ClientTimeout
from dis_snek import ComponentContext, InteractionContext, Member

from ElevatorBot.networking.errors import BackendException
from ElevatorBot.networking.results import BackendResult
from Shared.functions.ratelimiter import RateLimiter
from Shared.functions.readSettingsFile import get_setting
from Shared.networkingSchemas.base import CustomBaseModel

# the limiter object to not overload the backend
backend_limiter = RateLimiter(seconds=4, max_tokens=1000)
backend_semaphore = asyncio.Semaphore(200)
backend_cache = aiohttp_client_cache.RedisBackend(
    cache_name="elevator",
    address=f"""redis://{os.environ.get("REDIS_HOST")}:{os.environ.get("REDIS_PORT")}""",
    allowed_methods=["GET", "POST"] if not get_setting("ENABLE_DEBUG_MODE") else [],
    expire_after=0,  # only save selected stuff
    urls_expire_after={
        "**/destiny/account": timedelta(minutes=30),
        "**/destiny/activities/**/last": 0,  # never save last activity
        "**/destiny/activities/**/get/all": 0,  # never activity ids
        "**/destiny/activities/**/get/grandmaster": 0,  # never grandmaster ids
        "**/destiny/activities": timedelta(minutes=30),
        "**/destiny/items/lore/get/all": 0,  # never save lore ids
        "**/destiny/roles/*/*/get": timedelta(minutes=30),  # user roles
        "**/destiny/weapons/**/top": timedelta(minutes=60),  # user top weapons
        "**/destiny/weapons/**/weapon": timedelta(minutes=60),  # user weapon
    }
    if not get_setting("ENABLE_DEBUG_MODE")
    else {},
)
_no_default = object()


@dataclasses.dataclass(init=False)
class BaseBackendConnection:
    """
    Define default backend functions such as get, post and delete.
    These can be called by subclasses, and automatically handle networking and error handling
    """

    # used for error message formatting
    discord_member: Optional[Member]

    # used to send error messages
    ctx: Optional[InteractionContext | ComponentContext]

    # get logger
    logger: logging.Logger = dataclasses.field(
        default=logging.getLogger("backendNetworking"),
        init=False,
        compare=False,
        repr=False,
    )
    logger_exceptions: logging.Logger = dataclasses.field(
        default=logging.getLogger("backendNetworkingExceptions"),
        init=False,
        compare=False,
        repr=False,
    )

    # give request a max timeout of half an hour
    timeout: ClientTimeout = dataclasses.field(
        default=ClientTimeout(total=30 * 60),
        init=False,
        compare=False,
        repr=False,
    )

    # whether the ctx error message should be hidden
    hidden: bool = dataclasses.field(
        default=False,
        init=False,
        compare=False,
        repr=False,
    )

    # the rate limiter
    limiter: RateLimiter = dataclasses.field(
        default=backend_limiter,
        init=False,
        compare=False,
        repr=False,
    )
    semaphore: Semaphore = dataclasses.field(
        default=backend_semaphore,
        init=False,
        compare=False,
        repr=False,
    )

    # redis cache
    cache: aiohttp_client_cache.RedisBackend = dataclasses.field(
        default=backend_cache,
        init=False,
        compare=False,
        repr=False,
    )

    def __bool__(self):
        """Bool function to test if this exist. Useful for testing if this class got returned and not BackendResult, can be returned on errors"""

        return True

    async def send_error(self, result: BackendResult):
        """
        Send the error message

        Raises BackendException if there is an error
        """

        if self.ctx:
            if self.ctx.responded:
                raise RuntimeError("The context was already responded")
            await result.send_error_message(ctx=self.ctx, hidden=self.hidden)
        raise BackendException(result.error)

    async def _backend_request(
        self,
        method: str,
        route: str,
        params: Optional[dict] = None,
        data: Optional[dict | CustomBaseModel] = None,
        **error_message_kwargs,
    ) -> BackendResult:
        """Make a request to the specified backend route and return the results"""

        if data:
            # load with orjson to convert complex types such as datetime to a string
            if isinstance(data, CustomBaseModel):
                data = data.json()
            else:
                data = orjson.dumps(data)
            data = orjson.loads(data)

        await self.limiter.wait_for_token()

        async with self.semaphore:
            async with aiohttp_client_cache.CachedSession(
                cache=self.cache, timeout=self.timeout, json_serialize=lambda x: orjson.dumps(x).decode()
            ) as session:
                async with session.request(
                    method=method,
                    url=route,
                    params=params,
                    json=data,
                ) as response:
                    result = await self.__backend_parse_response(response=response)

                    # if an error occurred, already do the basic formatting
                    if not result:
                        if self.discord_member:
                            result.error_message = {"discord_member": self.discord_member}
                        if error_message_kwargs:
                            result.error_message = error_message_kwargs
                        await self.send_error(result)

                    return result

    async def __backend_parse_response(self, response: aiohttp.ClientResponse) -> BackendResult:
        """Handle any errors and then return the content of the response"""

        if response.status == 200:
            success = True
            error = None
            self.logger.info(f"{response.status}: `{response.method}` - `{response.url}`")

            # format the result to be the pydantic model
            result = await response.json(loads=orjson.loads)

        else:
            success = False
            result = None
            error = await self.__backend_handle_errors(response)

        return BackendResult(result=result, success=success, error=error)

    async def __backend_handle_errors(self, response: aiohttp.ClientResponse) -> Optional[str]:
        """Handles potential errors. Returns None if the error should not be returned to the user and str, str if something should be returned to the user"""

        match response.status:
            case 409:
                # this means the errors isn't really an error, and we want to return info to the user
                self.logger.info(f"{response.status}: `{response.method}` - `{response.url}`")
                error_json = await response.json(loads=orjson.loads)
                return error_json["error"]

            case 500:
                # internal server error
                self.logger_exceptions.error(f"{response.status}: `{response.method}` - `{response.url}`")
                return "ProgrammingError"

            case _:
                # if we don't know anything, just log it with the error
                self.logger_exceptions.error(
                    f"{response.status}: `{response.method}` - `{response.url}`\n{await response.json(loads=orjson.loads)}"
                )
                return None
