import logging

from naff import Client
from naff.client.errors import CommandCheckFailure

from ElevatorBot.discordEvents.base import ElevatorComponentContext, ElevatorInteractionContext
from ElevatorBot.misc.helperFunctions import log_error, parse_naff_errors
from ElevatorBot.networking.errors import BackendException


class CustomErrorClient(Client):
    # register the loggers
    logger_commands = logging.getLogger("commands")
    logger_commands_exceptions = logging.getLogger("commandsExceptions")

    logger_components = logging.getLogger("components")
    logger_components_exceptions = logging.getLogger("componentsExceptions")

    logger_exceptions = logging.getLogger("generalExceptions")

    async def on_error(self, source: str, error: Exception, *args, **kwargs):
        """Gets triggered after an error occurs (not in commands / components)"""

        naff_errors = parse_naff_errors(error=error)

        # log the error
        msg = f"Source `{source}`"
        if naff_errors:
            msg += f" - NAFF Errors:\n{naff_errors}"
        self.logger_exceptions.exception(msg, exc_info=error)

    async def on_command(self, ctx: ElevatorInteractionContext):
        """Gets triggered after a slash command is run"""

        # log the command
        self.logger_commands.info(
            f"InteractionID `{ctx.interaction_id}` - CommandName `/{ctx.invoked_name}` - Kwargs `{ctx.kwargs}` - DiscordName `{ctx.author.username}` - DiscordID `{ctx.author.id}` - GuildID `{ctx.guild.id}` - ChannelID `{ctx.channel.id}`"
        )

    async def on_command_error(self, ctx: ElevatorInteractionContext, error: Exception, *args, **kwargs):
        """Gets triggered on slash command errors"""

        # ignore some errors since they are intended
        if not isinstance(error, BackendException | CommandCheckFailure):
            await log_error(ctx=ctx, error=error, logger=self.logger_commands_exceptions)

    async def on_component(self, ctx: ElevatorInteractionContext):
        """Gets triggered after a component callback is run"""

        # log the command
        self.logger_components.info(
            f"InteractionID `{ctx.interaction_id}` - Component `{ctx.invoked_name}` - Target `{ctx.target_id}` - DiscordName `{ctx.author.username}` - DiscordID `{ctx.author.id}` - GuildID `{ctx.guild.id}` - ChannelID `{ctx.channel.id}`"
        )

    async def on_component_error(self, ctx: ElevatorComponentContext, error: Exception, *args, **kwargs):
        """Gets triggered on component callback errors"""

        # ignore BackendException errors since they are intended
        if not isinstance(error, BackendException):
            await log_error(ctx=ctx, error=error, logger=self.logger_components_exceptions)
