from dis_snek.models import (
    GuildChannel,
    GuildVoice,
    InteractionContext,
    OptionTypes,
    slash_command,
    slash_option,
)

from ElevatorBot.commandHelpers.responseTemplates import respond_wrong_channel_type
from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from settings import COMMAND_GUILD_SCOPE


class MemberCount(BaseScale):

    # todo perms
    @slash_command(
        **setup_sub_command,
        sub_cmd_name="member_count",
        sub_cmd_description="Select a voice channel that will show the member count",
        scopes=COMMAND_GUILD_SCOPE,
    )
    @slash_option(
        name="channel",
        description="The voice channel where the message should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
    )
    async def _member_count(self, ctx: InteractionContext, channel: GuildChannel):
        # make sure the channel is a voice channel
        if not isinstance(channel, GuildVoice):
            await respond_wrong_channel_type(ctx=ctx)
            return

        message_name = "member_count"
        success_message = f"The current member count will stay updated in {channel.mention}"
        await handle_setup_command(
            ctx=ctx, message_name=message_name, success_message=success_message, channel=channel, send_message=False
        )


def setup(client):
    MemberCount(client)
