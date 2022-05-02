import logging

from aiohttp import web

from ElevatorBot.webserver.routes.manifestUpdate import manifest_update
from ElevatorBot.webserver.routes.messages import messages
from ElevatorBot.webserver.routes.registration import registration
from ElevatorBot.webserver.routes.roles import roles
from ElevatorBot.webserver.routes.statusUpdate import status_update


@web.middleware
async def log_requests(request: web.Request, handler):
    try:
        response = await handler(request)

        # log the successful request
        logger = logging.getLogger("webServer")
        logger.info(f"`{response.status}`: `{request.path_qs}`")

        return response

    except Exception as error:
        if isinstance(error, web.HTTPClientError):
            raise error

        # log any errors
        logger = logging.getLogger("webServerExceptions")
        logger.error(
            f"""`{error}` for `{request.path_qs}` with body `{await request.json() if request.body_exists else ""}`""",
            exc_info=error,
        )


async def run_webserver(client):
    app = web.Application(middlewares=[log_requests])
    app.add_routes(
        [
            web.post("/registration", registration),
            web.post("/roles", roles),
            web.post("/messages", messages),
            web.post("/manifest_update", manifest_update),
            web.post("/status_update", status_update),
        ]
    )

    # all endpoints need access to the client
    app["client"] = client

    # do some trickery that we don't block the loop
    # web.run_app() is blocking
    # noinspection PyProtectedMember
    await web._run_app(app)
