from Shared.functions.logging import ElevatorLogger


def init_logging() -> None:
    # Initialize formatter
    logger = ElevatorLogger("Backend")

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
