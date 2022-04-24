from Backend.backgroundEvents.base import BaseEvent
from Backend.core.destiny.manifest import DestinyManifest
from Backend.database.base import acquire_db_session
from Backend.networking.elevatorApi import ElevatorApi


class ManifestUpdater(BaseEvent):
    """Check for Manifest Update hourly"""

    def __init__(self):
        interval_minutes = 60
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self):
        async with acquire_db_session() as db:
            manifest = DestinyManifest(db=db)

            # update
            post_elevator = await manifest.update()

        # populate the autocomplete options again because something changed
        if post_elevator:
            elevator_api = ElevatorApi()
            await elevator_api.post(route="/manifest_update")
