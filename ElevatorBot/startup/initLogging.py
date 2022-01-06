import logging
import os
import time
from typing import Optional


class MakeFileHandler(logging.FileHandler):
    def __init__(self, filename: str, mode: str = "a", encoding: Optional[str] = None, delay: bool = False):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)


def init_logging() -> None:
    def make_logger(log_name: str) -> None:
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(
            filename=f"./Logs/ElevatorBot/{log_name}.log",
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Initialize formatter
    formatter = logging.Formatter("%(asctime)s UTC || %(levelname)s || %(message)s")
    formatter.converter = time.gmtime

    # Initialize logging for discord events (on_member_add, etc.)
    make_logger("discordEvents")
    make_logger("generalExceptions")

    # Initialize logging for command usage
    make_logger("commands")
    make_logger("commandsExceptions")

    # Initialize logging for components usage
    make_logger("components")
    make_logger("componentsExceptions")

    # Initialize logging for registration
    make_logger("registration")

    # Initialize logging for background events
    make_logger("backgroundEvents")

    # Initialize logging for backend networking
    make_logger("backendNetworking")
