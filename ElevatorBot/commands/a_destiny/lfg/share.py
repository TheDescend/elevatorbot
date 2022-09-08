from naff import (
    Button,
    ButtonStyles,
    ChannelTypes,
    GuildText,
    Member,
    OptionTypes,
    Timestamp,
    TimestampStyles,
    slash_command,
    slash_option,
)
from naff.client.errors import Forbidden

from ElevatorBot.commandHelpers.optionTemplates import default_user_option, lfg_event_id
from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.destiny.lfg.lfgSystem import LfgMessage
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.discordShortcutFunctions import has_admin_permission
from ElevatorBot.misc.formatting import embed_message


class LfgShare(BaseModule):
    @slash_command(
        **lfg_sub_command,
        sub_cmd_name="share",
        sub_cmd_description="Share an event to a channel",
        dm_permission=False,
    )
    @lfg_event_id()
    @slash_option(
        name="channel",
        description="The text channel where the message should be displayed. Defaults to the current channel.",
        required=False,
        opt_type=OptionTypes.CHANNEL,
        channel_types=[ChannelTypes.GUILD_TEXT],
    )
    async def share(self, ctx: ElevatorInteractionContext, lfg_id: int, channel: GuildText = None):
        channel = channel or ctx.channel

        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(ctx=ctx, lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if not lfg_message:
            return

        timestamp = Timestamp.fromdatetime(lfg_message.start_time)
        message = await channel.send(
            embeds=embed_message(
                f"Sharing LFG Event",
                f"Activity: **{lfg_message.activity}**\nJoined: **{len(lfg_message.joined_ids)}/{lfg_message.max_joined_members}**\nStarting: {timestamp.format(style=TimestampStyles.ShortDateTime)} - {timestamp.format(style=TimestampStyles.RelativeTime)}",
            ),
            components=Button(
                style=ButtonStyles.URL,
                label="View Event",
                url=lfg_message.message.jump_url,
            ),
        )
        await ctx.send(
            embeds=embed_message("Success"),
            components=Button(
                style=ButtonStyles.URL,
                label="View Message",
                url=message.jump_url,
            ),
            ephemeral=True,
        )


def setup(client):
    LfgShare(client)
