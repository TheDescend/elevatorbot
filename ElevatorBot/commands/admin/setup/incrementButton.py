from dis_snek.models import (
    ActionRow,
    Button,
    ButtonStyles,
    ChannelTypes,
    GuildChannel,
    GuildText,
    InteractionContext,
    OptionTypes,
    slash_command,
    slash_option,
)

from ElevatorBot.commandHelpers.responseTemplates import respond_wrong_channel_type
from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.misc.formating import embed_message


class IncrementButton(BaseScale):

    # todo perms
    @slash_command(
        **setup_sub_command,
        sub_cmd_name="increment_button",
        sub_cmd_description="Creates a button that users can click and increment. Whoever gets the 69420 click wins",
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
    async def _increment_button(self, ctx: InteractionContext, channel: GuildChannel, message_id: str = None):
        message_name = "increment_button"
        components = [
            ActionRow(
                Button(
                    # todo callback
                    custom_id=message_name,
                    style=ButtonStyles.GREEN,
                    label="0",
                ),
            ),
        ]
        await handle_setup_command(
            ctx=ctx,
            message_name=message_name,
            channel=channel,
            send_message=True,
            send_components=components,
            send_message_embed=embed_message("Use the button to increase the count! Road to ram overflow!"),
            message_id=int(message_id) if message_id else None,
        )


def setup(client):
    IncrementButton(client)
