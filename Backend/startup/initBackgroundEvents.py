import logging

from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED,
    EVENT_JOB_REMOVED,
    EVENT_JOB_SUBMITTED,
    JobEvent,
    JobExecutionEvent,
    JobSubmissionEvent,
)
from apscheduler.job import Job

from Backend import backgroundEvents

event_name_by_id: dict[str, str] = {}


def register_background_events() -> int:
    """Adds all the events to apscheduler"""

    # gotta start the scheduler in the first place
    backgroundEvents.scheduler.start()

    # add listeners to catch and format errors and to send them to the log
    def event_added(scheduler_event: JobEvent):
        job: Job = backgroundEvents.scheduler.get_job(scheduler_event.job_id)

        # cache the name
        try:
            job_name = job.func.__self__.__class__.__name__
            event_name_by_id[scheduler_event.job_id] = job_name
        except AttributeError:
            event_name_by_id[scheduler_event.job_id] = job.func.__name__

        # log the execution
        logger = logging.getLogger("backgroundEvents")
        logger.info(f"Event `{job_name}` with ID `{scheduler_event.job_id}` has been added")

    backgroundEvents.scheduler.add_listener(event_added, EVENT_JOB_ADDED)

    def event_removed(scheduler_event: JobEvent):
        # log the execution
        logger = logging.getLogger("backgroundEvents")
        logger.info(
            f"Event `{event_name_by_id[scheduler_event.job_id]}` with ID `{scheduler_event.job_id}` has been removed"
        )

    backgroundEvents.scheduler.add_listener(event_removed, EVENT_JOB_REMOVED)

    def event_submitted(scheduler_event: JobSubmissionEvent):
        logger = logging.getLogger("backgroundEvents")
        logger.debug(
            f"Running event `{event_name_by_id[scheduler_event.job_id]}` with ID `{scheduler_event.job_id}`..."
        )

    backgroundEvents.scheduler.add_listener(event_submitted, EVENT_JOB_SUBMITTED)

    def event_executed(scheduler_event: JobExecutionEvent):
        event_name = event_name_by_id[scheduler_event.job_id]
        if event_name == "collect_prometheus_stats":
            return

        # log the execution
        logger = logging.getLogger("backgroundEvents")
        logger.info(f"Event `{event_name}` with ID `{scheduler_event.job_id}` successfully run")

    backgroundEvents.scheduler.add_listener(event_executed, EVENT_JOB_EXECUTED)

    def event_missed(scheduler_event: JobExecutionEvent):
        # log the execution
        logger = logging.getLogger("backgroundEventsExceptions")
        logger.warning(f"Event `{event_name_by_id[scheduler_event.job_id]}` with ID `{scheduler_event.job_id}` missed")

    backgroundEvents.scheduler.add_listener(event_missed, EVENT_JOB_MISSED)

    def event_error(scheduler_event: JobExecutionEvent):
        # log the execution
        logger = logging.getLogger("backgroundEventsExceptions")
        logger.exception(
            f"Event `{event_name_by_id[scheduler_event.job_id]}` with ID `{scheduler_event.job_id}` failed",
            exc_info=scheduler_event.exception,
        )

    backgroundEvents.scheduler.add_listener(event_error, EVENT_JOB_ERROR)

    # loop through the subclasses of BaseEvent to get all events. The events get imported through __init__
    event_logger = logging.getLogger("backgroundEvents")
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
            event_logger.debug(f"Failed to load event {event}")

    return len(backgroundEvents.scheduler.get_jobs())
