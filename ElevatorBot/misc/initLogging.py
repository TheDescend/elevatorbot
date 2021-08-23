import logging


def init_logging() -> None:
    def make_logger(log_name: str) -> None:
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(
            filename=f"logs/{log_name}.log",
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Initialize formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s : %(message)s")

    # Initialize logging for discord events (on_member_join, etc.)
    make_logger("discordEvents")

    # Initialize logging for command usage
    make_logger("commands")

    # Initialize logging for interaction usage
    make_logger("interactions")

    # Initialize logging for background events
    make_logger("backgroundEvents")

    # Initialize logging for backend networking
    make_logger("backendNetworking")
