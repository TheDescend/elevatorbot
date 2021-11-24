from aiohttp import web
from dis_snek.client import Snake

from ElevatorBot.misc.discordShortcutFunctions import (
    assign_roles_to_member,
    remove_roles_from_member,
)
from ElevatorBot.misc.status import update_events_status_message


async def status_update(request: web.Request):
    """
    Updates Elevators status page in descend - #admin-workboard
    Call with the event class name (CamelCase)

    Needs to be called with a json payload:
    {
        status_name: str
    }
    """

    event_name = (await request.json())["status_name"]

    await update_events_status_message(event_name=event_name)
