from dis_snek import ChannelTypes, GuildCategory, InteractionContext, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.subCommandTemplates import descend_setup_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.misc.cache import descend_cache
from settings import COMMAND_GUILD_SCOPE

# =============
# Descend Only!
# =============


class BoosterCount(BaseScale):

    # todo perms
    @slash_command(
        **descend_setup_sub_command,
        sub_cmd_name="booster_count",
        sub_cmd_description="Designate a voice channel that will always show the current booster count",
        scopes=COMMAND_GUILD_SCOPE,
    )
    @slash_option(
        name="category",
        description="The voice channel where the message should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
        channel_types=[ChannelTypes.GUILD_CATEGORY],
    )
    async def booster_count(self, ctx: InteractionContext, category: GuildCategory):
        # create the channel
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
