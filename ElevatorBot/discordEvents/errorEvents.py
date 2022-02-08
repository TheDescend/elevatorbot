import logging
import traceback

from dis_snek import ComponentContext, InteractionContext, Snake
from dis_snek.client.errors import CommandCheckFailure, HTTPException

from ElevatorBot.backendNetworking.errors import BackendException
from ElevatorBot.misc.helperFunctions import log_error


def parse_dis_snek_error(error: Exception, logger_exceptions: logging.Logger):
    """Parses dis-snek error messages and logs that"""

    if isinstance(error, HTTPException):
        if error.errors:
            # HTTPException's are of 3 known formats, we can parse them for human-readable errors
            try:
                errors = error.search_for_message(error.errors)
                formatted = f"HTTPException: {error.status}|{error.response.reason}: " + "\n".join(errors)
                logger_exceptions.error(formatted)
                print(formatted)
            except TypeError as e:
                print("Parsing Failed, errors are:")
                formatted = f"HTTPException: {error.status}|{error.response.reason}: {str(error.errors)}"
                logger_exceptions.error(formatted)
                print(formatted)
                pass


class CustomErrorSnake(Snake):
    # register the loggers
    logger_commands = logging.getLogger("commands")
    logger_commands_exceptions = logging.getLogger("commandsExceptions")

    logger_components = logging.getLogger("components")
    logger_components_exceptions = logging.getLogger("componentsExceptions")

    logger_events = logging.getLogger("discordEvents")
    logger_exceptions = logging.getLogger("generalExceptions")

    async def on_error(self, source: str, error: Exception, *args, **kwargs):
        """Gets triggered after an error occurs (not in commands / components)"""

        parse_dis_snek_error(error=error, logger_exceptions=self.logger_exceptions)

        # log the error
        self.logger_exceptions.exception(
            f"Source '{source}' - Error '{error}' - Traceback: \n{''.join(traceback.format_tb(error.__traceback__))}"
        )

        # raising error again to making deving easier
        raise error

    async def on_background_event_error(self, source: str, error: Exception, *args, **kwargs):
        """Gets triggered after an error occurs (not in commands / components)"""

        parse_dis_snek_error(error=error, logger_exceptions=self.logger_exceptions)

        # log the error
        self.logger_exceptions.exception(
            f"Source '{source}' - Error '{error}' - Traceback: \n{''.join(traceback.format_tb(error.__traceback__))}"
        )

        # raising error again to making deving easier
        raise error

    async def on_command(self, ctx: InteractionContext):
        """Gets triggered after a slash command is run"""

        if ctx.guild:
            # log the command
            self.logger_commands.info(
                f"InteractionID '{ctx.interaction_id}' - CommandName '/{ctx.invoked_name}' - Kwargs '{ctx.kwargs}' - DiscordName '{ctx.author.username}' - DiscordID '{ctx.author.id}' - GuildID '{ctx.guild.id}' - ChannelID '{ctx.channel.id}'"
            )

    async def on_command_error(self, ctx: InteractionContext, error: Exception, *args, **kwargs):
        """Gets triggered on slash command errors"""

        parse_dis_snek_error(error=error, logger_exceptions=self.logger_exceptions)

        # ignore some errors since they are intended
        if not isinstance(error, BackendException | CommandCheckFailure):
            await log_error(ctx=ctx, error=error, logger=self.logger_commands_exceptions)

    async def on_component(self, ctx: InteractionContext):
        """Gets triggered after a component callback is run"""

        # log the command
        self.logger_components.info(
            f"InteractionID '{ctx.interaction_id}' - Component '{ctx.invoked_name}' - Target '{ctx.target_id}' - DiscordName '{ctx.author.username}' - DiscordID '{ctx.author.id}' - GuildID '{ctx.guild.id}' - ChannelID '{ctx.channel.id}'"
        )

    async def on_component_error(self, ctx: ComponentContext, error: Exception, *args, **kwargs):
        """Gets triggered on component callback errors"""

        parse_dis_snek_error(error=error, logger_exceptions=self.logger_exceptions)

        # ignore BackendException errors since they are intended
        if not isinstance(error, BackendException):
            await log_error(ctx=ctx, error=error, logger=self.logger_components_exceptions)
