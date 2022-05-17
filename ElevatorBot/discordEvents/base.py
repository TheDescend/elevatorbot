from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ElevatorBot.discordEvents.errorEvents import CustomErrorClient


class ElevatorClient(CustomErrorClient):
    # register the scheduler for easier access
    scheduler = AsyncIOScheduler(timezone="UTC")
