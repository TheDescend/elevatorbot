import dataclasses
from typing import Optional

from dis_snek.errors import NotFound
from dis_snek.models import ActionRow, Embed, GuildChannel, InteractionContext, Message

from ElevatorBot.backendNetworking.errors import BackendException
from ElevatorBot.backendNetworking.misc.backendPersistentMessages import BackendPersistentMessages
from ElevatorBot.commandHelpers.responseTemplates import respond_wrong_author
from ElevatorBot.misc.formatting import embed_message


@dataclasses.dataclass()
class PersistentMessages(BackendPersistentMessages):
    async def get_channel_and_message(self) -> tuple[Optional[GuildChannel], Optional[Message]]:
        """Gets the channel and message"""

        result = await self.get()

        if result:
            channel = await self.guild.fetch_channel(result.channel_id)
            message = await channel.get_message(result.message_id) if channel else None

            return channel, message


async def handle_setup_command(
    ctx: InteractionContext,
    message_name: str,
    channel: GuildChannel,
    success_message: str = "None",
    send_message: bool = True,
    send_components: Optional[list[ActionRow]] = None,
    send_message_content: Optional[str] = None,
    send_message_embed: Optional[Embed] = None,
    message_id: Optional[int] = None,
) -> Optional[Message]:
    """Check stuff and then send the message and save it in the DB"""

    if send_message:
        assert send_message_content or send_message_embed

    # check that the message exists
    message = None
    if message_id:
        try:
            message = await channel.get_message(message_id)
            if message.author != message.guild.me:
                raise NotFound
        except NotFound:
            await respond_wrong_author(ctx=ctx, author_must_be=ctx.bot.user)
            return

    connection = PersistentMessages(ctx=None, guild=ctx.guild, message_name=message_name)
    connection.hidden = True
    try:
        old_data = await connection.get()
    except BackendException:
        old_data = None
    connection.ctx = ctx

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

    # delete the old message if that existed and is not the same message
    if old_data and old_data.message_id and old_data.message_id != message.id:
        old_channel = await ctx.bot.get_channel(old_data.channel_id)
        if old_channel:
            old_message = await old_channel.get_message(old_data.message_id)
            if old_message:
                await old_message.delete()

    # calculate the success message if that is not given
    if success_message == "None":
        success_message = f"Click [here]({message.jump_url}) to view the message"

    # send confirmation message if everything went well
    if result:
        await ctx.send(
            ephemeral=True,
            embeds=embed_message(
                "Success",
                success_message,
            ),
        )
        return message
