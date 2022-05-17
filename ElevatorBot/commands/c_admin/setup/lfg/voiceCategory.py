from naff import ChannelTypes, GuildChannel, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command, setup_sub_command_lfg_group
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.discordEvents.base import ElevatorInteractionContext


class LfgVoiceCategory(BaseModule):
    """
    Designate a category channel under which my LFG voice channels get created. If you want me to automatically create voice channels for each LFG event, use this to set it up
    """

    @slash_command(
        **setup_sub_command,
        **setup_sub_command_lfg_group,
        sub_cmd_name="voice_category",
        sub_cmd_description="Designate a category channel under which my LFG voice channels get created",
    )
    @slash_option(
        name="channel",
        description="The category channel where the voice channels should be anchored",
        required=True,
        opt_type=OptionTypes.CHANNEL,
        channel_types=[ChannelTypes.GUILD_CATEGORY],
    )
    @restrict_default_permission()
    async def voice_category(self, ctx: ElevatorInteractionContext, channel: GuildChannel):
        success_message = f"Future LFG events will have a voice channel created in {channel.mention}"
        await handle_setup_command(
            ctx=ctx,
            message_name="lfg_voice_category",
            success_message=success_message,
            channel=channel,
            send_message=False,
        )


def setup(client):
    LfgVoiceCategory(client)
