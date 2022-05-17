from naff import ChannelTypes, GuildCategory, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commandHelpers.subCommandTemplates import descend_setup_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.cache import descend_cache
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class BoosterCount(BaseModule):
    @slash_command(
        **descend_setup_sub_command,
        sub_cmd_name="booster_count",
        sub_cmd_description="Designate a voice channel that will always show the current booster count",
        dm_permission=False,
        scopes=get_setting("COMMAND_GUILD_SCOPE"),
    )
    @slash_option(
        name="category",
        description="The voice channel where the message should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
        channel_types=[ChannelTypes.GUILD_CATEGORY],
    )
    @restrict_default_permission()
    async def booster_count(self, ctx: ElevatorInteractionContext, category: GuildCategory):
        channel = await ctx.guild.create_voice_channel(
            name=f"Boosters｜{ctx.guild.premium_subscription_count}",
            category=category,
            reason="Booster Count Update",
        )

        message_name = "booster_count"
        success_message = f"The current booster count will stay updated in {channel.mention}"
        await handle_setup_command(
            ctx=ctx, message_name=message_name, success_message=success_message, channel=channel, send_message=False
        )

        # update the cache
        descend_cache.booster_count_channel = channel


def setup(client):
    BoosterCount(client)
