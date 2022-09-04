from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ElevatorBot.discordEvents.errorEvents import CustomErrorClient
from ElevatorBot.prometheus.client import StatsClient


class ElevatorClient(StatsClient, CustomErrorClient):
    # register the scheduler for easier access
    scheduler = AsyncIOScheduler(timezone="UTC")
