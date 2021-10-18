from dis_snek.models import InteractionContext
from dis_snek.models import SlashCommand

from ElevatorBot.misc.helperFunctions import log_error


class BaseInteractionCommand(SlashCommand):
    """Overwrites default events like on_error and pre_run"""

    def __attrs_post_init__(self):
        self.pre_run_callback = self.default_pre_run
        self.error_callback = self.default_error_handler

    async def default_pre_run(self, ctx: InteractionContext):
        """
        Default command that is run before the command is handled
        Checks if the member is registered
        """

        # todo
        ...

    async def default_error_handler(self, error: Exception, ctx: InteractionContext):
        """Default command that is run if a command errors out"""

        await log_error(ctx=ctx, error=error, situation="commands")
