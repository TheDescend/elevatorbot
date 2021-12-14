import logging
import traceback

from dis_snek import Snake
from dis_snek.models import ComponentContext, InteractionContext

from ElevatorBot.misc.helperFunctions import log_error


class CustomErrorSnake(Snake):
    # register the loggers
    logger_commands = logging.getLogger("commands")
    logger_commands_exceptions = logging.getLogger("commandsExceptions")

    logger_components = logging.getLogger("components")
    logger_components_exceptions = logging.getLogger("componentsExceptions")

    logger_events = logging.getLogger("discordEvents")
    logger_exceptions = logging.getLogger("commandsExceptions")

    async def on_error(self, source: str, error: Exception, *args, **kwargs):
        """Gets triggered after an error occurs (not in commands / components)"""

        # log the error
        self.logger_exceptions.exception(
            f"Source '{source}' - Error '{error}' - Traceback: \n{''.join(traceback.format_tb(error.__traceback__))}"
        )

        # raising error again to making deving easier
        raise error

    async def on_command(self, ctx: InteractionContext):
        """Gets triggered after a slash command is run"""

        # log the command
        self.logger_commands.info(
            f"InteractionID '{ctx.interaction_id}' - CommandName '/{ctx.invoked_name}' - Kwargs '{ctx.kwargs}' - DiscordName '{ctx.author.name}' - DiscordID '{ctx.author.id}' - GuildID '{ctx.guild.id}' - ChannelID '{ctx.channel.id}'"
        )

    async def on_command_error(self, ctx: InteractionContext, error: Exception, *args, **kwargs):
        """Gets triggered on slash command errors"""

        await log_error(ctx=ctx, error=error, logger=self.logger_commands_exceptions)

    async def on_component(self, ctx: InteractionContext):
        """Gets triggered after a component callback is run"""

        # log the command
        self.logger_components.info(
            f"InteractionID '{ctx.interaction_id}' - Component '{ctx.invoked_name}' - Target '{ctx.target_id}' - DiscordName '{ctx.author.name}' - DiscordID '{ctx.author.id}' - GuildID '{ctx.guild.id}' - ChannelID '{ctx.channel.id}'"
        )

    async def on_component_error(self, ctx: ComponentContext, error: Exception, *args, **kwargs):
        """Gets triggered on component callback errors"""

        await log_error(ctx=ctx, error=error, logger=self.logger_components_exceptions)
