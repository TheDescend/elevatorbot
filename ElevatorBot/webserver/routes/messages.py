from aiohttp import web

from ElevatorBot.misc.formatting import embed_message


async def messages(request: web.Request):
    """
    Sends a message in the specified guild and channel

    Needs to be called with a json payload:
    {
        "message": Optional[str],
        "embed_title": Optional[str],
        "embed_description": Optional[str],

        "guilds": [
            {
                "guild_id": int,
                "channel_id": int
            }
        ],
        ...
    }

    When the message field is empty, both embed fields must be supplied
    """

    client = request.app["client"]
    parameters = await request.json()

    guilds_with_errors = []

    # loop through the guilds where messages need to be send
    for guild_info in parameters["guilds"]:
        channel = await client.fetch_channel(guild_info["channel_id"])
        if not channel:
            guilds_with_errors.append(guild_info)
            continue

        embed = None
        if parameters["embed_title"]:
            embed = embed_message(parameters["embed_title"], parameters["embed_description"])
        await channel.send(content=parameters["message"], embeds=embed)

    return (
        web.json_response({"success": True})
        if not guilds_with_errors
        else web.json_response({"success": False, "guilds": guilds_with_errors})
    )
