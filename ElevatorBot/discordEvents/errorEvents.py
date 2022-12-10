import logging

from naff import Extension, listen
from naff.api import events
from naff.client.errors import CommandCheckFailure

from ElevatorBot.discordEvents.customInteractions import ElevatorComponentContext, ElevatorInteractionContext
from ElevatorBot.misc.helperFunctions import log_error, parse_naff_errors
from ElevatorBot.networking.errors import BackendException


class CustomErrorExtension(Extension):
    @listen()
    async def on_error(self, event: events.Error):
        """Gets triggered after an error occurs (not in commands / components)"""

        naff_errors = parse_naff_errors(error=event.error)

        # log the error
        msg = f"Source `{event.source}`"
        if naff_errors:
            msg += f" - NAFF Errors:\n{naff_errors}"
        self.bot.logger_exceptions.exception(msg, exc_info=event.error)

    @listen()
    async def on_command_completion(self, event: events.CommandCompletion):
        """Gets triggered after a slash command is run"""

        # log the command
        self.bot.logger_commands.info(
            f"InteractionID `{event.ctx.interaction_id}` - CommandName `/{event.ctx.invoked_name}` - Kwargs `{event.ctx.kwargs}` - DiscordName `{event.ctx.author.username}` - DiscordID `{event.ctx.author.id}` - GuildID `{event.ctx.guild.id}` - ChannelID `{event.ctx.channel.id}`"
        )

    @listen()
    async def on_command_error(self, event: events.CommandError):
        """Gets triggered on slash command errors"""

        # ignore some errors since they are intended
        if not isinstance(event.error, BackendException | CommandCheckFailure):
            await log_error(ctx=event.ctx, error=event.error, logger=self.bot.logger_commands_exceptions)

    @listen()
    async def on_component_completion(self, event: events.ComponentCompletion):
        """Gets triggered after a component callback is run"""

        # log the command
        self.bot.logger_components.info(
            f"InteractionID `{event.ctx.interaction_id}` - Component ID `{event.ctx.custom_id}` - Target `{event.ctx.target_id}` - DiscordName `{event.ctx.author.username}` - DiscordID `{event.ctx.author.id}` - GuildID `{event.ctx.guild.id}` - ChannelID `{event.ctx.channel.id}`"
        )

    @listen()
    async def on_component_error(self, event: events.ComponentError):
        """Gets triggered on component callback errors"""

        # ignore BackendException errors since they are intended
        if not isinstance(event.error, BackendException):
            await log_error(ctx=event.ctx, error=event.error, logger=self.bot.logger_components_exceptions)


def setup(client):
    CustomErrorExtension(client)
