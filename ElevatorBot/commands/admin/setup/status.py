from dis_snek.models import (
    ChannelTypes,
    GuildChannel,
    InteractionContext,
    OptionTypes,
    slash_command,
    slash_option,
)

from ElevatorBot.commandHelpers.subCommandTemplates import descend_setup_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.misc.cache import descend_cache
from ElevatorBot.misc.formating import embed_message
from settings import COMMAND_GUILD_SCOPE

# =============
# Descend Only!
# =============


class Status(BaseScale):
    # todo perms
    @slash_command(
        **descend_setup_sub_command,
        sub_cmd_name="status",
        sub_cmd_description="Designate a channel in which status messages get posted and updated",
        scopes=COMMAND_GUILD_SCOPE,
    )
    @slash_option(
        name="channel",
        description="The text channel where the message should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
        channel_types=[ChannelTypes.GUILD_TEXT],
    )
    @slash_option(
        name="message_id",
        description="You can input a message ID (needs to be from me and selected channel) to have me edit that message",
        required=False,
        opt_type=OptionTypes.STRING,
    )
    async def _status(self, ctx: InteractionContext, channel: GuildChannel, message_id: str = None):
        message_name = "status"
        embed = embed_message("Status: Last valid...")
        embed.set_footer("Updated")
        message = await handle_setup_command(
            ctx=ctx,
            message_name=message_name,
            channel=channel,
            send_message=True,
            send_message_embed=embed,
            message_id=int(message_id) if message_id else None,
        )

        if message:
            # cache that
            descend_cache.status_message = message


def setup(client):
    Status(client)
