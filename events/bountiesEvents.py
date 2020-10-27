from events.base_event import BaseEvent
from functions.bounties.bountiesFunctions import bountyCompletion


# check if players have completed a bounty
class checkBountyCompletion(BaseEvent):
    def __init__(self):
        interval_minutes = 30  # Set the interval for this event
        super().__init__(interval_minutes)

    async def run(self, client):
        await bountyCompletion(client)

