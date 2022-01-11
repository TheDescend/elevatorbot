from Shared.functions.logging import ElevatorLogger


def init_logging() -> None:
    # Initialize formatter
    logger = ElevatorLogger("Backend")

    # Initialize logging for incoming requests
    logger.make_logger("requests")
    logger.make_logger("exceptions")

    # Initialize logging for external api requests
    logger.make_logger("bungieApi")
    logger.make_logger("elevatorApi")

    # Initialize logging for Background Events
    logger.make_logger("backgroundEvents")
    logger.make_logger("updateActivityDb")
