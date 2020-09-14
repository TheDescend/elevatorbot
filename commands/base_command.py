from static.config import COMMAND_PREFIX


# Base command class
# Do not modify!
class BaseCommand:

    def __init__(self, description, params, topic="Misc"):
        self.name = type(self).__name__.lower()
        self.params = params

        desc = f"`{COMMAND_PREFIX}{self.name}`"

        if self.params:
            desc += " " + " ".join(f"*<{p}>*" for p in params)

        desc += f": {description}."
        self.description = desc
        self.topic = topic

    # Every command must override this method
    async def handle(self, params, message, client):
        raise NotImplementedError  # To be defined by every command
