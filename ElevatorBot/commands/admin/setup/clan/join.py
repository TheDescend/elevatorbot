from dis_snek.models import (
    ActionRow,
    Button,
    ButtonStyles,
    ChannelTypes,
    GuildChannel,
    InteractionContext,
    OptionTypes,
    slash_command,
    slash_option,
)

from ElevatorBot.commandHelpers.subCommandTemplates import (
    setup_sub_command,
    setup_sub_command_clan_group,
)
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command


class ClanJoin(BaseScale):
    """Designate a channel where players can join your clan by pressing a button. They will get an invite by the person which used /setup clan link"""

    # todo perms
    @slash_command(
        **setup_sub_command,
        **setup_sub_command_clan_group,
        sub_cmd_name="join",
        sub_cmd_description="Designate a channel where players can join your clan by pressing a button",
    )
    @slash_option(
        name="channel",
        description="The text channel where the message should be displayed",
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
    async def _join(self, ctx: InteractionContext, channel: GuildChannel, message_id: str = None):
        message_name = "clan_join_request"
        components = [
            ActionRow(
                Button(
                    # todo callback
                    custom_id=message_name,
                    style=ButtonStyles.GREEN,
                    label="Click to Join the Linked Destiny 2 Clan",
                ),
            ),
        ]
        await handle_setup_command(
            ctx=ctx,
            message_name=message_name,
            channel=channel,
            send_message=True,
            send_components=components,
            send_message_content="⁣",
            message_id=int(message_id) if message_id else None,
        )


def setup(client):
    ClanJoin(client)
