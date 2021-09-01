import discord
from aiohttp import web

from ElevatorBot.webserver.routes.register import register


async def run_webserver(client: discord.Client):
    app = web.Application()
    app.add_routes([web.post('/register', register)])

    # all endpoints need access to the client
    app['client'] = client

    # do some trickery that we don't block the loop
    # web.run_app() is blocking
    await web._run_app(app)
