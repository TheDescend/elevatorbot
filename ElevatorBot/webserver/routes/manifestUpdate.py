from aiohttp import web

from ElevatorBot.commandHelpers import autocomplete
from ElevatorBot.startup.initAutocompleteOptions import load_autocomplete_options


async def manifest_update(request: web.Request):
    """
    Update the autocomplete options after a manifest update
    """
    client = request.app["client"]

    # delete old data
    autocomplete.activities_grandmaster = {}
    autocomplete.activities = {}
    autocomplete.activities_by_id = {}
    autocomplete.weapons = {}
    autocomplete.weapons_by_id = {}
    autocomplete.lore = {}
    autocomplete.lore_by_id = {}

    # refill it
    await load_autocomplete_options(client=client)

    return web.json_response({"success": True})
