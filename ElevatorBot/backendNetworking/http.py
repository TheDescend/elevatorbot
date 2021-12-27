import asyncio
import dataclasses
import logging
import time
from typing import Optional

import aiohttp
import orjson
from aiohttp import ClientSession, ClientTimeout
from dis_snek.models import ComponentContext, InteractionContext
from dis_snek.models.discord_objects.user import Member
from pydantic import BaseModel

from ElevatorBot.backendNetworking.errors import BackendException
from ElevatorBot.backendNetworking.results import BackendResult


# the limiter object to not overload the backend
class BackendRateLimiter:
    RATE = 250
    MAX_TOKENS = 10000

    def __init__(self):
        self.tokens = self.MAX_TOKENS
        self.updated_at = time.monotonic()

    async def wait_for_token(self):
        """waits until a token becomes available"""
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(0.1)
        assert self.tokens >= 1
        self.tokens -= 1

    def add_new_tokens(self):
        """Adds a new token if eligible"""
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.RATE
        if self.tokens + new_tokens >= 1:
            self.tokens = min(self.tokens + new_tokens, self.MAX_TOKENS)
            self.updated_at = now


backend_limiter = BackendRateLimiter()
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
    limiter: BackendRateLimiter = dataclasses.field(
        default=backend_limiter,
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
        data: Optional[dict | BaseModel] = None,
        **error_message_kwargs,
    ) -> BackendResult:
        """Make a request to the specified backend route and return the results"""

        if data:
            # load with orjson to convert complex types such as datetime to a string
            if isinstance(data, BaseModel):
                data = data.json()
            else:
                data = orjson.dumps(data)
            data = orjson.loads(data)

        async with asyncio.Lock():
            await self.limiter.wait_for_token()

            async with ClientSession(
                timeout=self.timeout, json_serialize=lambda x: orjson.dumps(x).decode()
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
                            result.error_message = {"discord_member": self.discord_member, **error_message_kwargs}
                        await self.send_error(result)

                    return result

    async def __backend_parse_response(self, response: aiohttp.ClientResponse) -> BackendResult:
        """Handle any errors and then return the content of the response"""

        if response.status == 200:
            success = True
            error = None
            self.logger.info("%s: '%s' - '%s'", response.status, response.method, response.url)

            # format the result to be the pydantic model
            result = await response.json(loads=orjson.loads)

        else:
            success = False
            result = None
            error = await self.__backend_handle_errors(response)

        return BackendResult(result=result, success=success, error=error)

    async def __backend_handle_errors(self, response: aiohttp.ClientResponse) -> Optional[str]:
        """Handles potential errors. Returns None if the error should not be returned to the user and str, str if something should be returned to the user"""

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
