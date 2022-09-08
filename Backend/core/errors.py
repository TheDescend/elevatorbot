from bungio.error import (
    AuthenticationTooSlow,
    BadRequest,
    BungieDead,
    BungieException,
    BungIOException,
    HttpException,
    InvalidAuthentication,
    NotFound,
    TimeoutException,
)
from fastapi import Request
from starlette.responses import JSONResponse


class CustomException(Exception):
    """
    Define a exception which we raise on errors where ElevatorBot should return that info to the user
    The response to the error gets defined in ElevatorBot/static/errorCodesAndResponses.py
    """

    def __init__(
        self,
        error: str = "ProgrammingError",
    ):
        self.error = error


async def handle_custom_exception(request: Request, exception: CustomException):
    return JSONResponse(
        status_code=409,
        content={
            "error": exception.error,
        },
    )


async def handle_bungio_exception(request: Request, exception: HttpException):
    content = {}
    if isinstance(exception, InvalidAuthentication):
        error = "NoToken"
    elif isinstance(exception, NotFound):
        error = "BungieBadRequest"
    elif isinstance(exception, BadRequest):
        error = "BungieBadRequest"
    elif isinstance(exception, AuthenticationTooSlow):
        error = "BungieUnauthorized"
    elif isinstance(exception, (BungieDead, TimeoutException)):
        error = "BungieDed"
    else:
        error = exception.error
        content["message"] = exception.message
    content["error"] = error

    return JSONResponse(
        status_code=409,
        content=content,
    )
