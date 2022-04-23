from aiohttp import web

from ElevatorBot.commandHelpers import autocomplete
from ElevatorBot.startup.initAutocompleteOptions import load_autocomplete_options


async def manifest_update(request: web.Request):
    """
    Update the autocomplete options after a manifest update
    """

    # refill data
    await load_autocomplete_options()

    return web.json_response({"success": True})
