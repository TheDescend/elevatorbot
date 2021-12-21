from ElevatorBot.misc.status import update_events_status_message


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
            self.run_date = kwargs["run_date"]  # datetime(2000, 2, 20, 19, 30, 50)

    async def call(self, client):
        """Run the post event functions"""

        await self.run(client=client)

        # update status message
        await update_events_status_message(event_name=type(self).__name__)

    async def run(self, client):
        """Every event must override this method"""
        raise NotImplementedError
