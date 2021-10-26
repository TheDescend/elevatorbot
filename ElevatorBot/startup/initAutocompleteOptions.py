from dis_snek.client import Snake

from ElevatorBot.backendNetworking.destiny.activities import DestinyActivities
from ElevatorBot.commandHelpers.autocomplete import (
    DestinyActivityModel,
    activities,
    activities_by_id,
)


async def load_autocomplete_options(client: Snake):
    """Fetch the needed data from the DB"""

    # loop through them all and add them to the global activities dict
    db_activities = await DestinyActivities(discord_member=None, client=None, discord_guild=None).get_all()
    for activity in db_activities.result["activities"]:
        model = DestinyActivityModel(
            name=activity["name"],
            description=activity["description"],
            activity_ids=activity["activity_ids"],
        )
        activities.update({model.name.lower(): model})
        for activity_id in model.activity_ids:
            activities_by_id.update({activity_id: model})
