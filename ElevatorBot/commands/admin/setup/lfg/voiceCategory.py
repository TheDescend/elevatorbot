from dis_snek.models import (
    GuildCategory,
    GuildChannel,
    InteractionContext,
    OptionTypes,
    slash_command,
    slash_option,
)

from ElevatorBot.commandHelpers.responseTemplates import respond_wrong_channel_type
from ElevatorBot.commandHelpers.subCommandTemplates import (
    setup_sub_command,
    setup_sub_command_lfg_group,
)
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command


class LfgVoiceCategory(BaseScale):

    # todo perms
    @slash_command(
        **setup_sub_command,
        **setup_sub_command_lfg_group,
        sub_cmd_name="voice_category",
        sub_cmd_description="The category channel in which the LFG voice channel are created",
    )
    @slash_option(
        name="channel",
        description="The category channel where the voice channels should be anchored",
        required=True,
        opt_type=OptionTypes.CHANNEL,
    )
    async def _voice_category(self, ctx: InteractionContext, channel: GuildChannel):
        # make sure the channel is a text channel
        if not isinstance(channel, GuildCategory):
            await respond_wrong_channel_type(ctx=ctx, channel_must_be="category")
            return

        success_message = f"Future LFG posts will have a voice channel created in {channel.mention}"
        await handle_setup_command(
            ctx=ctx,
            message_name="lfg_voice_category",
            success_message=success_message,
            channel=channel,
            send_message=False,
        )


def setup(client):
    LfgVoiceCategory(client)
