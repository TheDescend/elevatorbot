# Base event class
# Do not modify!
class BaseEvent:
    def __init__(self, **kwargs):
        if "scheduler_type" in kwargs:
            # default type which can be overwritten. Options are interval, cron, date
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

    # Every event must override this method
    async def run(self, client):
        raise NotImplementedError  # To be defined by every event
