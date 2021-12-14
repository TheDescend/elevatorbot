from aiohttp import web

from ElevatorBot.elevator import ElevatorSnake
from ElevatorBot.misc.discordShortcutFunctions import (
    assign_roles_to_member,
    remove_roles_from_member,
)


async def roles(request: web.Request):
    """
    Assigns the specified roles to the specified user in the specified guild

    Needs to be called with a json payload:
    {
        data: [
            "discord_id": int,
            "guild_id": int,
            "to_assign_role_ids": Optional[list[int]],
            "to_remove_role_ids": Optional[list[int]],
        ],
        ...
    }
    """

    client: ElevatorSnake = request.app["client"]
    parameters = await request.json()

    # get mutual guilds
    mutual_guild_ids = [
        guild.id for guild in (await client.get_user(parameters["data"][0]["discord_id"])).mutual_guilds
    ]

    # loop through the guilds where roles need to be assigned
    for data in parameters["data"]:
        if data["guild_id"] in mutual_guild_ids:
            guild = await client.get_guild(data["guild_id"])
            member = await guild.get_member(data["discord_id"])

            if data["to_assign_role_ids"]:
                await assign_roles_to_member(member, *data["to_assign_role_ids"])
            if data["to_remove_role_ids"]:
                await remove_roles_from_member(member, *data["to_remove_role_ids"])

    return web.json_response({"success": True})
