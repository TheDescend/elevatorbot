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

from ElevatorBot import backgroundEvents
from ElevatorBot.core.destiny.lfg.lfgSystem import LfgMessage
from ElevatorBot.discordEvents.errorEvents import parse_naff_errors
from ElevatorBot.networking.destiny.lfgSystem import DestinyLfgSystem
from Shared.functions.readSettingsFile import get_setting

event_name_by_id: dict[str, str] = {}


async def register_background_events(client):
    """Adds all the events to apscheduler"""

    # gotta start the scheduler in the first place
    client.scheduler.start()

    # add listeners to catch and format errors and to send them to the log
    def event_added(scheduler_event: JobEvent):
        job: Job = client.scheduler.get_job(scheduler_event.job_id)

        # cache the name
        job_name = job.func.__self__.__class__.__name__
        event_name_by_id[scheduler_event.job_id] = job_name

        # log the execution
        logger = logging.getLogger("backgroundEvents")
        logger.info(f"Event `{job_name}` with ID `{scheduler_event.job_id}` has been added")

    client.scheduler.add_listener(event_added, EVENT_JOB_ADDED)

    def event_removed(scheduler_event: JobEvent):
        # log the execution
        logger = logging.getLogger("backgroundEvents")
        logger.info(
            f"Event `{event_name_by_id[scheduler_event.job_id]}` with ID `{scheduler_event.job_id}` has been removed"
        )

    client.scheduler.add_listener(event_removed, EVENT_JOB_REMOVED)

    def event_submitted(scheduler_event: JobSubmissionEvent):
        logger = logging.getLogger("backgroundEvents")
        logger.debug(
            f"Running event `{event_name_by_id[scheduler_event.job_id]}` with ID `{scheduler_event.job_id}`..."
        )

    client.scheduler.add_listener(event_submitted, EVENT_JOB_SUBMITTED)

    def event_executed(scheduler_event: JobExecutionEvent):
        # log the execution
        logger = logging.getLogger("backgroundEvents")
        logger.info(
            f"Event `{event_name_by_id[scheduler_event.job_id]}` with ID `{scheduler_event.job_id}` successfully run"
        )

    client.scheduler.add_listener(event_executed, EVENT_JOB_EXECUTED)

    def event_missed(scheduler_event: JobExecutionEvent):
        # log the execution
        logger = logging.getLogger("backgroundEventsExceptions")
        logger.warning(f"Event `{event_name_by_id[scheduler_event.job_id]}` with ID `{scheduler_event.job_id}` missed")

    client.scheduler.add_listener(event_missed, EVENT_JOB_MISSED)

    def event_error(scheduler_event: JobExecutionEvent):
        # log the execution
        naff_errors = parse_naff_errors(error=scheduler_event.exception)
        msg = f"Event `{event_name_by_id[scheduler_event.job_id]}` with ID `{scheduler_event.job_id}` failed"
        if naff_errors:
            msg += f" - NAFF Errors:\n{naff_errors}"

        logger = logging.getLogger("backgroundEventsExceptions")
        logger.exception(msg, exc_info=scheduler_event.exception)

    client.scheduler.add_listener(event_error, EVENT_JOB_ERROR)

    # loop through the subclasses of BaseEvent to get all events. The events get imported through .__init__
    event_logger = logging.getLogger("backgroundEvents")
    for BackgroundEvent in backgroundEvents.BaseEvent.__subclasses__():
        event = BackgroundEvent()

        # check the type of job and schedule accordingly
        if event.scheduler_type == "interval":
            client.scheduler.add_job(
                func=event.call,
                trigger="interval",
                args=(client,),
                minutes=event.interval_minutes,
                jitter=5 * 60 if not get_setting("ENABLE_DEBUG_MODE") else None,
            )
        elif event.scheduler_type == "cron":
            client.scheduler.add_job(
                func=event.call,
                trigger="cron",
                args=(client,),
                day_of_week=event.dow_day_of_week,
                hour=event.dow_hour,
                minute=event.dow_minute,
            )
        elif event.scheduler_type == "date":
            client.scheduler.add_job(
                func=event.call,
                trigger="date",
                args=(client,),
                run_date=event.run_date,
            )
        else:
            event_logger.debug(f"Failed to load event {event}")
    jobs = client.scheduler.get_jobs()
    event_logger.debug(f"< {len(jobs)} > Background Events Loaded")

    # load the lfg events
    for guild in client.guilds:
        backend = DestinyLfgSystem(
            ctx=None,
            discord_guild=guild,
        )

        # get all lfg ids
        result = await backend.get_all()
        if result:
            events = result.events

            # create the objs from the returned data
            for event in events:
                lfg_event = await LfgMessage.from_lfg_output_model(
                    client=client, model=event, backend=backend, guild=guild
                )

                # add the event
                if lfg_event:
                    await lfg_event.schedule_event()

    logger.debug(f"< {len(client.scheduler.get_jobs()) - len(jobs)} > LFG Events Loaded")
