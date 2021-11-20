from fastapi import Request
from starlette.responses import JSONResponse


class CustomException(Exception):
    """
    Define a exception which we raise on errors where ElevatorBot should return that info to the user
    The response to the error gets defined in ElevatorBot/static/errorCodesAndResponses.py
    """

    def __init__(
        self,
        error: str,
    ):
        self.error = error


async def handle_custom_exception(request: Request, exception: CustomException):
    # todo log that maybe

    return JSONResponse(
        status_code=409,
        content={
            "error": exception.error,
        },
    )
