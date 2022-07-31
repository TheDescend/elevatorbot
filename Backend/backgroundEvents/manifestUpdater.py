from Backend.backgroundEvents.base import BaseEvent
from Backend.bungio.client import get_bungio_client


class ManifestUpdater(BaseEvent):
    """Check for Manifest Update hourly"""

    def __init__(self):
        interval_minutes = 60
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self):
        # noinspection PyProtectedMember
        await get_bungio_client().manifest._check_for_updates()
