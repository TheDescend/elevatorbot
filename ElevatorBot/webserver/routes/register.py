import discord

from aiohttp import web


async def register(request: web.Request):
    """Send a message in the channel where the user has just finished their registration"""
    client: discord.Client = request.app['client']

    parameters = await request.json()

    print(parameters)
    await client.get_channel(670570955290181675).send("Hi from websocket")

    return web.Response(text="Elevator now has a webserver, look in discord")
