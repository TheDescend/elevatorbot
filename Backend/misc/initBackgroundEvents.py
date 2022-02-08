import logging

from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED,
    EVENT_JOB_REMOVED,
    EVENT_JOB_SUBMITTED,
)

from Backend import backgroundEvents


def register_background_events() -> int:
    """Adds all the events to apscheduler"""

    # gotta start the scheduler in the first place
    backgroundEvents.scheduler.start()

    # add listeners to catch and format errors and to send them to the log
    def event_added(scheduler_event):
        job = backgroundEvents.scheduler.get_job(scheduler_event.job_id)

        # log the execution
        logger = logging.getLogger("backgroundEvents")
        logger.info(f"Event '{job.func.__name__}' with ID '{scheduler_event.job_id}' has been added")

    backgroundEvents.scheduler.add_listener(event_added, EVENT_JOB_ADDED)

    def event_removed(scheduler_event):
        logger = logging.getLogger("backgroundEvents")
        logger.info(f"Event with ID '{scheduler_event.job_id}' has been removed")

    backgroundEvents.scheduler.add_listener(event_removed, EVENT_JOB_REMOVED)

    def event_submitted(scheduler_event):
        job = backgroundEvents.scheduler.get_job(scheduler_event.job_id)

        print(f"Running '{job.func.__name__}' with ID '{scheduler_event.job_id}'")

    backgroundEvents.scheduler.add_listener(event_submitted, EVENT_JOB_SUBMITTED)

    def event_executed(scheduler_event):
        job = backgroundEvents.scheduler.get_job(scheduler_event.job_id)

        # log the execution
        logger = logging.getLogger("backgroundEvents")
        logger.info(f"Event '{job.func.__name__}' successfully run")

    backgroundEvents.scheduler.add_listener(event_executed, EVENT_JOB_EXECUTED)

    def event_missed(scheduler_event):
        job = backgroundEvents.scheduler.get_job(scheduler_event.job_id)

        # log the execution
        logger = logging.getLogger("backgroundEventsExceptions")
        logger.warning(f"Event '{job.func.__name__}' missed")

    backgroundEvents.scheduler.add_listener(event_missed, EVENT_JOB_MISSED)

    def event_error(scheduler_event):
        job = backgroundEvents.scheduler.get_job(scheduler_event.job_id)

        # log the execution
        logger = logging.getLogger("backgroundEventsExceptions")
        logger.error(
            f"Event '{job.func.__name__}' failed - Error '{ scheduler_event.exception}' - Traceback: \n{scheduler_event.traceback}"
        )

    backgroundEvents.scheduler.add_listener(event_error, EVENT_JOB_ERROR)

    # loop through the subclasses of BaseEvent to get all events. The events get imported through __init__
    for BackgroundEvent in backgroundEvents.BaseEvent.__subclasses__():
        event = BackgroundEvent()

        # check the type of job and schedule accordingly
        if event.scheduler_type == "interval":
            backgroundEvents.scheduler.add_job(
                func=event.call,
                trigger="interval",
                minutes=event.interval_minutes,
                jitter=15 * 60,
            )
        elif event.scheduler_type == "cron":
            backgroundEvents.scheduler.add_job(
                func=event.call,
                trigger="cron",
                day_of_week=event.dow_day_of_week,
                hour=event.dow_hour,
                minute=event.dow_minute,
            )
        elif event.scheduler_type == "date":
            backgroundEvents.scheduler.add_job(
                func=event.call,
                trigger="date",
                run_date=event.run_date,
            )
        else:
            print(f"Failed to load event {event}")

    return len(backgroundEvents.scheduler.get_jobs())
