import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ElevatorBot.prometheus.client import StatsClient


class ElevatorClient(StatsClient):
    # register the loggers
    logger_commands = logging.getLogger("commands")
    logger_commands_exceptions = logging.getLogger("commandsExceptions")

    logger_components = logging.getLogger("components")
    logger_components_exceptions = logging.getLogger("componentsExceptions")

    logger_exceptions = logging.getLogger("generalExceptions")

    # register the scheduler for easier access
    scheduler = AsyncIOScheduler(timezone="UTC")
