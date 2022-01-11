from Shared.functions.logging import ElevatorLogger


def init_logging() -> None:
    # Initialize formatter
    logger = ElevatorLogger("ElevatorBot")

    # Initialize logging for discord events (on_member_add, etc.)
    logger.make_logger("discordEvents")
    logger.make_logger("generalExceptions")

    # Initialize logging for command usage
    logger.make_logger("commands")
    logger.make_logger("commandsExceptions")

    # Initialize logging for components usage
    logger.make_logger("components")
    logger.make_logger("componentsExceptions")

    # Initialize logging for registration
    logger.make_logger("registration")

    # Initialize logging for background events
    logger.make_logger("backgroundEvents")

    # Initialize logging for backend networking
    logger.make_logger("backendNetworking")
