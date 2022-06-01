import logging

from Shared.functions.logging import ColourHighlighter, ElevatorLogger


def init_logging() -> None:
    # Initialize lib loggers
    ElevatorLogger.make_console_logger(
        logger=logging.getLogger("fastapi"),
        level=logging.NOTSET,
        highlighter=ColourHighlighter(name="fastapi", colour="purple"),
    )
    ElevatorLogger.make_console_logger(
        logger=logging.getLogger("uvicorn"),
        level=logging.NOTSET,
        highlighter=ColourHighlighter(name="uvicorn", colour="yellow"),
    )
    ElevatorLogger.make_console_logger(
        logger=logging.getLogger("uvicorn.access"),
        level=logging.NOTSET,
        highlighter=ColourHighlighter(name="uvicorn", colour="yellow"),
    )
    ElevatorLogger.make_console_logger(
        logger=logging.getLogger("sqlalchemy"),
        level=logging.NOTSET,
        highlighter=ColourHighlighter(name="sqlalchemy", colour="red"),
    )

    # Initialize formatter
    logger = ElevatorLogger("Backend")

    # Initialize logging for roles
    logger.make_logger("roles")

    # Initialize logging for incoming requests
    logger.make_logger("requests")
    logger.make_logger("requestsExceptions")

    # Initialize logging for external api requests
    logger.make_logger("bungieApi")
    logger.make_logger("bungieApiExceptions")

    logger.make_logger("elevatorApi")
    logger.make_logger("elevatorApiExceptions")

    # Initialize logging for Background Events
    logger.make_logger("backgroundEvents")
    logger.make_logger("backgroundEventsExceptions")

    # Initialize logging for activity DB updates
    logger.make_logger("updateActivityDb")
    logger.make_logger("updateActivityDbExceptions")

    # Initialize logging for registrations
    logger.make_logger("registration")
