from ElevatorBot.backendNetworking.errors import BackendException
from ElevatorBot.backgroundEvents.base import BaseEvent
from ElevatorBot.discordEvents.base import ElevatorSnake
from ElevatorBot.misc.cache import descend_cache
from ElevatorBot.static.descendOnlyIds import descend_channels


class BoosterCountUpdater(BaseEvent):
    """This updates the booster count for descend"""

    def __init__(self):
        interval_minutes = 30
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self, client: ElevatorSnake):
        # get the channel if exists and update that message
        try:
            channel = await descend_cache.get_booster_count()
        except BackendException:
            return

        # update the name
        await channel.edit(
            name=f"Boosters｜{descend_channels.guild.premium_subscription_count}",
            reason="Booster Count Update",
        )
