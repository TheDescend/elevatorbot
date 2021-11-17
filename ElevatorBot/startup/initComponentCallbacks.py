from dis_snek import Snake
from dis_snek.models import ComponentCommand

from ElevatorBot.components.componentCallbacks import ComponentCallbacks


def add_component_callbacks(client: Snake):
    """Add global custom component callbacks"""

    # get all functions from the class. Magic
    for custom_id in [k for k in ComponentCallbacks.__dict__ if not k.startswith("__")]:
        client.add_component_callback(
            ComponentCommand(
                name=f"ComponentCallback::{custom_id}",
                callback=getattr(ComponentCallbacks, custom_id),
                listeners=[custom_id],
            )
        )
