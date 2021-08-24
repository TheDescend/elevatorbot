import logging

import discord
import pytz
from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED,
    EVENT_JOB_REMOVED,
    EVENT_JOB_SUBMITTED,
)

from ElevatorBot import backgroundEvents


def register_background_events(client: discord.Client) -> int:
    """Adds all the events to apscheduler"""

    # gotta start the scheduler in the first place
    backgroundEvents.scheduler.start()

    # add listeners to catch and format errors and to send them to the log
    def event_added(scheduler_event):
        job_name = backgroundEvents.scheduler.get_job(scheduler_event.job_id)

        # log the execution
        logger = logging.getLogger("backgroundEvents")
        logger.info("Event '%s' with ID '%s' has been added", job_name, scheduler_event.job_id)

    backgroundEvents.scheduler.add_listener(event_added, EVENT_JOB_ADDED)

    def event_removed(scheduler_event):
        # log the execution
        logger = logging.getLogger("backgroundEvents")
        logger.info("Event with ID '%s' has been removed", scheduler_event.job_id)

    backgroundEvents.scheduler.add_listener(event_removed, EVENT_JOB_REMOVED)

    def event_submitted(scheduler_event):
        job_name = backgroundEvents.scheduler.get_job(scheduler_event.job_id)
        print(f"Running '{job_name}'")

    backgroundEvents.scheduler.add_listener(event_submitted, EVENT_JOB_SUBMITTED)

    def event_executed(scheduler_event):
        job_name = backgroundEvents.scheduler.get_job(scheduler_event.job_id)

        # log the execution
        logger = logging.getLogger("backgroundEvents")
        logger.info("Event '%s' successfully run", job_name)

    backgroundEvents.scheduler.add_listener(event_executed, EVENT_JOB_EXECUTED)

    def event_missed(scheduler_event):
        job_name = backgroundEvents.scheduler.get_job(scheduler_event.job_id)

        # log the execution
        logger = logging.getLogger("backgroundEvents")
        logger.warning("Event '%s' missed", job_name)

    backgroundEvents.scheduler.add_listener(event_missed, EVENT_JOB_MISSED)

    def event_error(scheduler_event):
        job_name = backgroundEvents.scheduler.get_job(scheduler_event.job_id)

        # log the execution
        logger = logging.getLogger("backgroundEvents")
        logger.error(
            "Event '%s' failed - Error '%s' - Traceback: \n%s",
            job_name,
            scheduler_event.exception,
            scheduler_event.traceback,
        )

    backgroundEvents.scheduler.add_listener(event_error, EVENT_JOB_ERROR)

    # loop through the subclasses of BaseEvent to get all events. The events get imported through misc.__init__
    for BackgroundEvent in backgroundEvents.BaseEvent.__subclasses__():
        event = BackgroundEvent()

        # check the type of job and schedule accordingly
        if event.scheduler_type == "interval":
            backgroundEvents.scheduler.add_job(
                func=event.run,
                trigger="interval",
                args=(client,),
                minutes=event.interval_minutes,
                jitter=60,
            )
        elif event.scheduler_type == "cron":
            backgroundEvents.scheduler.add_job(
                func=event.run,
                trigger="cron",
                args=(client,),
                day_of_week=event.dow_day_of_week,
                hour=event.dow_hour,
                minute=event.dow_minute,
                timezone=pytz.utc,
            )
        elif event.scheduler_type == "date":
            backgroundEvents.scheduler.add_job(
                func=event.run,
                trigger="date",
                args=(client,),
                run_date=event.run_date,
                timezone=pytz.utc,
            )
        else:
            print(f"Failed to load event {event}")

    return len(backgroundEvents.scheduler.get_jobs())
