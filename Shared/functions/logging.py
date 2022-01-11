import dataclasses
import logging
import os
import time
from typing import Optional


class ElevatorLogger:
    def __init__(self, path: str):
        self.formatter = logging.Formatter("%(asctime)s UTC || %(levelname)s || %(message)s")
        self.formatter.converter = time.gmtime

        self.path = path

    def make_logger(self, log_name: str):
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.DEBUG)

        file_handler = MakeFileHandler(
            filename=f"./Logs/{self.path}/{log_name}.log",
            encoding="utf-8",
        )
        file_handler.setFormatter(self.formatter)
        logger.addHandler(file_handler)


class MakeFileHandler(logging.FileHandler):
    def __init__(self, filename: str, mode: str = "a", encoding: Optional[str] = None, delay: bool = False):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)
