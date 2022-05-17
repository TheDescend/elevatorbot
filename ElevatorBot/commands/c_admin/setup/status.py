from naff import ChannelTypes, GuildChannel, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commandHelpers.subCommandTemplates import descend_setup_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.cache import descend_cache
from ElevatorBot.misc.formatting import embed_message
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class Status(BaseModule):
    @slash_command(
        **descend_setup_sub_command,
        sub_cmd_name="status",
        sub_cmd_description="Designate a channel in which status messages get posted and updated",
        scopes=get_setting("COMMAND_GUILD_SCOPE"),
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
    @restrict_default_permission()
    async def status(self, ctx: ElevatorInteractionContext, channel: GuildChannel, message_id: str = None):
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
