from aiohttp import web
from dis_snek.models import User

from ElevatorBot.elevator import ElevatorSnake
from ElevatorBot.misc.cache import registered_role_cache
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.emojis import custom_emojis


async def registration(request: web.Request):
    """
    Send a message to the user that the registration was successful

    Needs to be called with a json payload:
    {
        "discord_id": int,
    }
    """
    client: ElevatorSnake = request.app["client"]

    # get discord object
    parameters = await request.json()
    user: User = await client.get_user(parameters["discord_id"])

    # get emoji
    enter_emoji = custom_emojis.enter
    elevator_emoji = custom_emojis.elevator_logo

    await user.send(
        embeds=embed_message(
            "Registration",
            f"{elevator_emoji} **You have registered successfully, thank you!** {elevator_emoji}\n⁣\n{enter_emoji}Registration is global, so you do not need to re-register, when you join a new server where I am also present\n{enter_emoji}If you want to link a different Destiny Account, just `/register` again",
        )
    )

    # update the cache
    if user.id in registered_role_cache.not_registered_users:
        registered_role_cache.not_registered_users.pop(user.id)

    # reply with the guilds the user is in
    # that's needed for the role assignment
    guild_ids = [guild.id for guild in user.mutual_guilds]

    return web.json_response({"guild_ids": guild_ids})
