from naff import ActionRow, Button, ButtonStyles, ChannelTypes, GuildChannel, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.discordEvents.base import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message


class IncrementButton(BaseModule):

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
        description="You can input a message ID (needs to be from me and selected channel) to have me edit that message",
        required=False,
        opt_type=OptionTypes.STRING,
    )
    async def increment_button(self, ctx: ElevatorInteractionContext, channel: GuildChannel, message_id: str = None):
        if ctx.author.id != 238388130581839872:
            await ctx.send(
                "This is blocked for now, since it it waiting for a vital unreleased discord feature", ephemeral=True
            )
            return

        message_name = "increment_button"
        components = [
            ActionRow(
                Button(
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
            send_message_embed=embed_message(
                "Button Up Already", "Use the button to increase the count! Road to ram overflow!"
            ),
            message_id=int(message_id) if message_id else None,
        )


def setup(client):
    IncrementButton(client)
