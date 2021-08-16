import logging


def init_logging():
    # Initialize formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s : %(message)s")

    def make_logger(log_name):
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(f"logs/{log_name}.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Initialize logging for command usage
    make_logger("commands")
    make_logger("slashCommands")
    make_logger("events")

    make_logger("update_activity_db")
    make_logger("network")
