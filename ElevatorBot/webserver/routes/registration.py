from aiohttp import web
from naff import User

from ElevatorBot.misc.cache import registered_role_cache
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.static.emojis import custom_emojis


async def registration(request: web.Request):
    """
    Send a message to the user that the registration was successful

    Needs to be called with a json payload:
    {
        "discord_id": int,
    }
    """
    client = request.app["client"]

    # get discord object
    parameters = await request.json()
    user: User = await client.fetch_user(parameters["discord_id"])

    # get emoji
    enter_emoji = custom_emojis.enter
    elevator_emoji = custom_emojis.elevator_logo

    await user.send(
        embeds=embed_message(
            "Registration",
            f"""{elevator_emoji} **You have registered successfully, thank you!** {elevator_emoji}\n⁣\n{enter_emoji} Registration is global, so you do not need to re-register, when you join a new server where I am also present\n{enter_emoji} If you want to link a different Destiny Account, just {client.get_command_by_name("register").mention()} again""",
        )
    )

    # reply with the guilds the user is in
    # that's needed for the role assignment
    return web.json_response({"success": True, "guild_ids": [guild.id for guild in user.mutual_guilds]})
