import discord
from aiohttp import web

from ElevatorBot.misc.discordShortcutFunctions import assign_roles_to_member, remove_roles_from_member


async def roles(request: web.Request):
    """
    Assigns the specified roles to the specified user in the specified guild

    Needs to be called with a json payload:
    {
        data: [
            "discord_id": int,
            "guild_id": int,
            "to_assign_role_id": Optional[list[int]],
            "to_remove_role_id": Optional[list[int]],
        ],
        ...
    }
    """

    client: discord.Client = request.app["client"]
    parameters = await request.json()

    # loop through the guilds where roles need to be assigned
    for data in parameters["data"]:
        guild = client.get_guild(data["guild_id"])
        member = guild.get_member(data["discord_id"])

        if data["to_assign_role_id"]:
            await assign_roles_to_member(member, *data["to_assign_role_id"])
        if data["to_remove_role_id"]:
            await remove_roles_from_member(member, *data["to_remove_role_id"])


    return web.json_response({"success": True})
