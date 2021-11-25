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
from settings import COMMAND_GUILD_SCOPE


class BoosterCount(BaseScale):

    # todo perms
    @slash_command(
        **descend_setup_sub_command,
        sub_cmd_name="booster_count",
        sub_cmd_description="Designate a voice channel that will always show the current booster count",
        scopes=COMMAND_GUILD_SCOPE,
    )
    @slash_option(
        name="channel",
        description="The voice channel where the message should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
        channel_types=[ChannelTypes.GUILD_VOICE],
    )
    async def _booster_count(self, ctx: InteractionContext, channel: GuildChannel):
        message_name = "booster_count"
        success_message = f"The current booster count will stay updated in {channel.mention}"
        await handle_setup_command(
            ctx=ctx, message_name=message_name, success_message=success_message, channel=channel, send_message=False
        )

        # update the cache
        descend_cache.booster_count_channel = channel


def setup(client):
    BoosterCount(client)
