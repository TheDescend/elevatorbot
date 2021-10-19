from aiohttp import web
from dis_snek.client import Snake
from dis_snek.models import User

from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.emojis import elevator_logo_emoji_id
from ElevatorBot.static.emojis import enter_emoji_id


async def registration(request: web.Request):
    """
    Send a message to the user that the registration was successful

    Needs to be called with a json payload:
    {
        "discord_id": int,
    }
    """
    client: Snake = request.app["client"]

    # get discord object
    parameters = await request.json()
    user: User = await client.get_user(parameters["discord_id"])

    # get emoji
    enter_emoji = client.get_emoji(enter_emoji_id)
    elevator_emoji = client.get_emoji(elevator_logo_emoji_id)

    await user.send(
        embeds=embed_message(
            "Registration",
            f"{elevator_emoji} **You have registered successfully, thank you!** {elevator_emoji}\n⁣\n{enter_emoji}Registration is global, so you do not need to re-register, when you join a new server where I am also present\n{enter_emoji}If you want to link a different Destiny Account, just `/register` again",
        )
    )

    # reply with the guilds the user is in
    # that's needed for the role assignment
    guild_ids = [guild.id for guild in user.mutual_guilds]

    return web.json_response({"guild_ids": guild_ids})
