from Backend.backgroundEvents.base import BaseEvent
from Backend.networking.bungieApi import bungie_client


class ManifestUpdater(BaseEvent):
    """Check for Manifest Update hourly"""

    def __init__(self):
        interval_minutes = 60
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self):
        # noinspection PyProtectedMember
        await bungie_client.manifest._check_for_updates()
