from dis_snek import ChannelTypes, GuildCategory, InteractionContext, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.subCommandTemplates import descend_setup_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.misc.cache import descend_cache
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class MemberCount(BaseScale):

    # todo perms
    @slash_command(
        **descend_setup_sub_command,
        sub_cmd_name="member_count",
        sub_cmd_description="Designate a voice channel that will always show the current member count",
        scopes=get_setting("COMMAND_GUILD_SCOPE"),
    )
    @slash_option(
        name="category",
        description="The voice channel where the message should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
        channel_types=[ChannelTypes.GUILD_CATEGORY],
    )
    async def member_count(self, ctx: InteractionContext, category: GuildCategory):
        # create the channel
        channel = await ctx.guild.create_voice_channel(
            name=f"Members｜{ctx.guild.member_count}",
            category=category,
            reason="Member Count Update",
        )

        message_name = "member_count"
        success_message = f"The current member count will stay updated in {channel.mention}"
        await handle_setup_command(
            ctx=ctx, message_name=message_name, success_message=success_message, channel=channel, send_message=False
        )

        # update the cache
        descend_cache.member_count_channel = channel


def setup(client):
    MemberCount(client)
