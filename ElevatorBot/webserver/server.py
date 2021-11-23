from aiohttp import web
from dis_snek.client import Snake

from ElevatorBot.webserver.routes.manifestUpdate import manifest_update
from ElevatorBot.webserver.routes.messages import messages
from ElevatorBot.webserver.routes.registration import registration
from ElevatorBot.webserver.routes.roles import roles


async def run_webserver(client: Snake):
    app = web.Application()
    app.add_routes(
        [
            web.post("/registration", registration),
            web.post("/roles", roles),
            web.post("/messages", messages),
            web.post("/manifest_update", manifest_update),
        ]
    )

    # all endpoints need access to the client
    app["client"] = client

    # do some trickery that we don't block the loop
    # web.run_app() is blocking
    await web._run_app(app)
