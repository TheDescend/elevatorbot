from dis_snek.models import (
    GuildChannel,
    GuildText,
    InteractionContext,
    OptionTypes,
    slash_option,
    sub_command,
)

from ElevatorBot.commandHelpers.responseTemplates import respond_wrong_channel_type
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.misc.formating import embed_message
from settings import COMMAND_GUILD_SCOPE


class Status(BaseScale):
    # todo maybe use websocket to get backend updates and display them in discord
    # todo perms
    @sub_command(
        base_name="setup",
        base_description="Use these commands to setup ElevatorBot on this server",
        sub_name="status",
        sub_description="The channel in which the status messages get posted and updated",
        scope=COMMAND_GUILD_SCOPE,
    )
    @slash_option(
        name="channel",
        description="The text channel where the message should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
    )
    @slash_option(
        name="message_id",
        description="You can input a message ID to have me edit that message instead of sending a new one. Message must be from me and in the input channel",
        required=False,
        opt_type=OptionTypes.INTEGER,
    )
    async def _status(self, ctx: InteractionContext, channel: GuildChannel, message_id: int = None):
        # make sure the channel is a text channel
        if not isinstance(channel, GuildText):
            await respond_wrong_channel_type(ctx=ctx)
            return

        message_name = "_status"
        embed = embed_message("Status: Last valid...")
        await handle_setup_command(
            ctx=ctx,
            message_name=message_name,
            channel=channel,
            send_message=True,
            send_message_embed=embed,
            message_id=message_id,
        )


def setup(client):
    Status(client)
