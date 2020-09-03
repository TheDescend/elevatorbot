from events.base_event import BaseEvent
from functions.bounties.bountiesFunctions   import updateLeaderboard
from functions.bounties.bountiesBackend     import bountyCompletion


# update the leaderboard every 60 mins
class refreshBountiesLeaderboards(BaseEvent):
    def __init__(self):
        interval_minutes = 60  # Set the interval for this event
        super().__init__(interval_minutes)

    def run(self, client):
        updateLeaderboard(client)


# check if players have completed a bounty
class checkBountyCompletion(BaseEvent):
    def __init__(self):
        interval_minutes = 60  # Set the interval for this event
        super().__init__(interval_minutes)

    async def run(self, client):
        await bountyCompletion(client)

