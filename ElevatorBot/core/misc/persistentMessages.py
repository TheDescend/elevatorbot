import dataclasses
from typing import Optional

from dis_snek.errors import NotFound
from dis_snek.models import (
    ActionRow,
    Button,
    ButtonStyles,
    Embed,
    GuildChannel,
    GuildText,
    InteractionContext,
    Message,
)

from ElevatorBot.backendNetworking.misc.backendPersistentMessages import (
    BackendPersistentMessages,
)
from ElevatorBot.commandHelpers.responseTemplates import (
    respond_wrong_author,
    respond_wrong_channel_type,
)
from ElevatorBot.misc.formating import embed_message


@dataclasses.dataclass()
class PersistentMessages(BackendPersistentMessages):
    async def get_channel_and_message(self) -> tuple[Optional[GuildChannel], Optional[Message]]:
        """Gets the channel and message"""

        result = await self._get()

        if result:
            channel = await self.guild.get_channel(result.result["channel_id"])
            message = await channel.get_message(result.result["message_id"]) if channel else None

            return channel, message


async def handle_setup_command(
    ctx: InteractionContext,
    message_name: str,
    channel: GuildChannel,
    success_message: str = "None",
    send_message: bool = True,
    send_components: list[ActionRow] = None,
    send_message_content: str = None,
    send_message_embed: Embed = None,
    message_id: int = None,
):
    """Check stuff and then send the message and save it in the DB"""

    if send_message:
        assert send_message_content or send_message_embed

    # check that the message if from me
    message = None
    if message_id:
        try:
            message = await channel.get_message(message_id)
            if message.author != ctx.bot.user:
                raise NotFound
        except NotFound:
            await respond_wrong_author(ctx=ctx, author_must_be=ctx.bot.user)
            return

    connection = PersistentMessages(guild=ctx.guild, message_name=message_name)

    # send the message
    if send_message:
        if message:
            await message.edit(components=send_components, content=send_message_content, embeds=send_message_embed)
        else:
            message = await channel.send(
                components=send_components, content=send_message_content, embeds=send_message_embed
            )

        result = await connection.upsert(channel_id=channel.id, message_id=message.id)

    else:
        result = await connection.upsert(channel_id=channel.id)

    # calculate the success message if that is not given
    if success_message is "None":
        if send_components:
            success_message = f"Click [here]({message.jump_url}) to view the message"

    # send confirmation message if everything went well
    if result:
        await ctx.send(
            ephemeral=True,
            embeds=embed_message(
                f"Success",
                success_message,
            ),
        )
    else:
        await result.send_error_message(ctx=ctx, hidden=True)
