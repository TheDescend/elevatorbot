import dataclasses
import logging
import os
import time
from importlib import import_module
from typing import Optional

from rich.highlighter import Highlighter
from rich.logging import RichHandler
from rich.text import Text

DESCEND_COLOUR = "#71b093"


def try_import(name: str):
    try:
        import_module(name)
    except ModuleNotFoundError:
        pass
    else:
        to_suppress.append(name)


# try to import the libs to suppress here
to_suppress = ["dis-snek", "sqlalchemy", "pydantic", "fastapi", "asyncpg", "aiohttp"]
for lib in []:
    try_import(lib)

RICH_LOGGING_PARAMS = {
    "show_time": True,
    "omit_repeated_times": False,
    "show_level": True,
    "show_path": True,
    "enable_link_path": True,
    "markup": True,
    "rich_tracebacks": True,
    "tracebacks_show_locals": True,
    "tracebacks_suppress": to_suppress,
    "log_time_format": "[%d/%m/%Y %H:%M:%S]",
}


@dataclasses.dataclass
class ColourHighlighter(Highlighter):
    name: str = "Other"
    colour: str = "yellow"

    # noinspection PyProtectedMember
    def highlight(self, text: Text):
        plain = text.plain

        # make code blocks nicer
        result = []
        first = True
        for char in plain:
            if char == "`":
                result.append("[bold][italic]" if first else "[/bold][/italic]")
                first = not first
            else:
                result.append(char)
        plain = "".join(result)

        new_text = Text.assemble((f"[{self.name.upper()}] ", self.colour), Text.from_markup(plain))
        text._text = new_text._text
        text._spans = new_text._spans
        text._length = new_text._length


# overwrite default logging behaviour. don't judge, it works
default_handler = RichHandler(
    **RICH_LOGGING_PARAMS,
    highlighter=ColourHighlighter(),
)
logging.getLogger().handlers = [default_handler]


def getLogger(name=None):  # noqa
    if not name or isinstance(name, str) and name == logging.root.name:
        return logging.root
    logger = logging.Logger.manager.getLogger(name)

    if not logger.propagate:
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                logger.removeHandler(handler)
        if not logger.handlers:
            logger.addHandler(default_handler)
    else:
        logger.handlers = []
    return logger


def addHandler(self, hdlr):  # noqa
    if self.propagate:
        return

    if isinstance(hdlr, logging.StreamHandler) and not isinstance(hdlr, logging.FileHandler):
        hdlr = default_handler  # noqa

    logging._acquireLock()  # noqa
    try:
        if not (hdlr in self.handlers):
            self.handlers.append(hdlr)
    finally:
        logging._releaseLock()  # noqa


logging.getLogger = getLogger
logging.Logger.addHandler = addHandler


class ElevatorLogger:
    """Log most logging events to a file, and log all events to console"""

    def __init__(self, path: str):
        self.path = path
        self.highlighter = ColourHighlighter(name=self.path.upper().replace("BOT", ""), colour=DESCEND_COLOUR)

    @staticmethod
    def make_console_logger(
        logger: logging.Logger, highlighter: Optional[Highlighter] = None, level: int = logging.DEBUG
    ):
        logger.propagate = False
        console_handler = RichHandler(
            **RICH_LOGGING_PARAMS,
            level=level,
            highlighter=highlighter,
        )
        logger.handlers = []
        logger.addHandler(console_handler)

    def make_logger(self, log_name: str, only_console: bool = False):
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.DEBUG)

        # log to console (DEBUG)
        self.make_console_logger(logger=logger, highlighter=self.highlighter)

        # log to file (INFO)
        if not only_console:
            file_handler = MakeFileHandler(
                filename=f"./Logs/{self.path}/{log_name}.log",
                encoding="utf-8",
            )
            file_formatter = logging.Formatter("%(asctime)s UTC || %(levelname)s || %(message)s")
            file_formatter.converter = time.gmtime
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.INFO)
            logger.addHandler(file_handler)


class MakeFileHandler(logging.FileHandler):
    def __init__(self, filename: str, mode: str = "a", encoding: Optional[str] = None, delay: bool = False):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        super().__init__(filename, mode, encoding, delay)
