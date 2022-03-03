from aiohttp import web
from dis_snek.api.events import GuildLeft
from dis_snek.client.errors import Forbidden

from ElevatorBot.backendNetworking.errors import BackendException
from ElevatorBot.backendNetworking.misc.elevatorInfo import ElevatorGuilds
from ElevatorBot.discordEvents.guildEvents import on_guild_left
from ElevatorBot.misc.discordShortcutFunctions import assign_roles_to_member, remove_roles_from_member


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

    client = request.app["client"]
    parameters = await request.json()

    # loop through the guilds where roles need to be assigned
    for data in parameters["data"]:
        # make sure both the guild and the member can be not found anymore
        try:
            if not (guild := await client.fetch_guild(data["guild_id"])):
                await on_guild_left(GuildLeft(guild_id=data["guild_id"]))
                continue

        except Forbidden:
            continue

        if not (member := await guild.fetch_member(data["discord_id"])):
            continue

        if data["to_assign_role_ids"]:
            await assign_roles_to_member(member, *data["to_assign_role_ids"])
        if data["to_remove_role_ids"]:
            await remove_roles_from_member(member, *data["to_remove_role_ids"])

    return web.json_response({"success": True})
