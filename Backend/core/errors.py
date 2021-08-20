from fastapi import Request
from starlette.responses import JSONResponse



class CustomException(Exception):
    """ Define a exception which we raise on errors where ElevatorBot should return that info to the user """

    def __init__(
        self,
        error: str,
        error_message: str
    ):
        self.error = error
        self.error_message = error_message


async def handle_custom_exception(request: Request, exception: CustomException):
    return JSONResponse(
        status_code=409,
        content={
            "error": exception.error,
            "message": exception.error_message
        },
    )
