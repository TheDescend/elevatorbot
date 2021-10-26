from dis_snek.models import (
    GuildChannel,
    GuildText,
    InteractionContext,
    OptionTypes,
    slash_command,
    slash_option,
)

from ElevatorBot.commandHelpers.responseTemplates import respond_wrong_channel_type
from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command


class BungieRssFeed(BaseScale):

    # todo perms
    @slash_command(
        **setup_sub_command,
        sub_cmd_name="bungie_feed",
        sub_cmd_description="Links your own Destiny 2 clan with this discord. Requires Admin in both Discord and Destiny",
    )
    @slash_option(
        name="channel",
        description="The text channel where the messages should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
    )
    @slash_option(
        name="message",
        description="You can input a message ID to have me edit that message instead of sending a new one. Message must be from me and in the input channel",
        required=False,
        opt_type=OptionTypes.INTEGER,
    )
    async def _bungie_rss_feed(self, ctx: InteractionContext, channel: GuildChannel):
        # make sure the channel is a text channel
        if not isinstance(channel, GuildText):
            await respond_wrong_channel_type(ctx=ctx)
            return

        success_message = f"Future Bungie Updates will be posted in {channel.mention}"
        await handle_setup_command(
            ctx=ctx,
            message_name="rss",
            success_message=success_message,
            channel=channel,
            send_message=False,
        )


def setup(client):
    BungieRssFeed(client)
