from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ElevatorBot.discordEvents.errorEvents import CustomErrorSnake


class ElevatorSnake(CustomErrorSnake):
    # register the scheduler for easier access
    scheduler = AsyncIOScheduler(timezone="UTC")
