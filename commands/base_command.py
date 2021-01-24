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
        else:
            self.params = []

        desc += f": {description}."
        self.description = desc
        self.topic = topic

    # Every command must override this method
    async def handle(self, params, message, mentioned_user, client):
        """
        params : list of command args besides the command itself
        message : discord.message instance of the command
        mentioned_user : discord.user instance of @user. otherwise instance of message.author
        client : discord bot instance
        """

        raise NotImplementedError  # To be defined by every command
