from apscheduler.schedulers.asyncio import AsyncIOScheduler

from Backend.networking.elevatorApi import ElevatorApi

scheduler = AsyncIOScheduler(timezone="UTC")


class BaseEvent:
    def __init__(self, **kwargs):
        if "scheduler_type" in kwargs:
            # options are interval, cron, date
            self.scheduler_type = kwargs["scheduler_type"]

        if self.scheduler_type == "interval":
            # interval
            # The event will run every interval_minutes minutes
            # https://apscheduler.readthedocs.io/en/stable/modules/triggers/interval.html
            self.interval_minutes = kwargs["interval_minutes"]  # 10

        elif self.scheduler_type == "cron":
            # cron
            # what day / time it will run at
            # https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
            self.dow_day_of_week = kwargs["dow_day_of_week"]  # "mon"
            self.dow_hour = kwargs["dow_hour"]  # 10
            self.dow_minute = kwargs["dow_minute"]  # 55

        elif self.scheduler_type == "date":
            # date
            # https://apscheduler.readthedocs.io/en/stable/modules/triggers/date.html
            self.run_date = kwargs["run_date"]

    async def call(self):
        """Run the post event functions"""

        await self.run()

        # update elevator status message
        elevator_api = ElevatorApi()
        await elevator_api.post(route="/status_update", json={"status_name": type(self).__name__})

    async def run(self):
        """Every event must override this method"""
        raise NotImplementedError
