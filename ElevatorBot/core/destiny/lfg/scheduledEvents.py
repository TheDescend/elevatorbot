from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def delete_lfg_scheduled_events(event_scheduler: AsyncIOScheduler, event_ids: list[int | str]):
    """Removes all scheduled events"""

    for event_id in event_ids:
        try:
            event_scheduler.remove_job(str(event_id))
        except JobLookupError:
            pass
