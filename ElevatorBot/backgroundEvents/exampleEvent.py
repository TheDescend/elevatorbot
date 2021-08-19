from ElevatorBot.backgroundEvents import BaseEvent


class ExampleEvent(BaseEvent):
    """ Print something every hour """


    def __init__(
        self
    ):
        interval_minutes = 60
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)


    async def run(
        self,
        client
    ):
        print("Printed from a background event")
