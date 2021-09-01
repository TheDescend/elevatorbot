import discord
from aiohttp import web

from ElevatorBot.webserver.routes.registration import registration
from ElevatorBot.webserver.routes.roles import roles


async def run_webserver(client: discord.Client):
    app = web.Application()
    app.add_routes([
        web.post('/registration', registration),
        web.post('/roles', roles),
    ])

    # all endpoints need access to the client
    app['client'] = client

    # do some trickery that we don't block the loop
    # web.run_app() is blocking
    await web._run_app(app)
