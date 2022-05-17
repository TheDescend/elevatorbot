from naff import ChannelTypes, GuildChannel, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext


class BungieRssFeed(BaseModule):
    @slash_command(
        **setup_sub_command,
        sub_cmd_name="bungie_feed",
        sub_cmd_description="Designate a channel where bungie articles get posted",
        dm_permission=False,
    )
    @slash_option(
        name="channel",
        description="The text channel where the messages should be displayed",
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
    async def bungie_feed(self, ctx: ElevatorInteractionContext, channel: GuildChannel, message_id: str = None):
        success_message = f"Future Bungie Updates will be posted in {channel.mention}"
        await handle_setup_command(
            ctx=ctx,
            message_name="rss",
            success_message=success_message,
            channel=channel,
            send_message=False,
            message_id=int(message_id) if message_id else None,
        )


def setup(client):
    BungieRssFeed(client)
