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

from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command


class Registration(BaseScale):

    # todo perms
    @slash_command(
        **setup_sub_command,
        sub_cmd_name="registration",
        sub_cmd_description="Setup a channel in which user can register with me by pressing a button",
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
        description="You can input a message ID to have me edit that message instead of sending a new one. Message must be from me and in the input channel",
        required=False,
        opt_type=OptionTypes.STRING,
    )
    async def _registration(self, ctx: InteractionContext, channel: GuildChannel, message_id: str = None):
        message_name = "registration"
        components = [
            ActionRow(
                Button(
                    # todo callback
                    custom_id=message_name,
                    style=ButtonStyles.GREEN,
                    label="Click to Connect your Destiny 2 Account",
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
    Registration(client)
