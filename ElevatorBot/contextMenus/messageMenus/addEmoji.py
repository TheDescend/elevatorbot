import io

import aiohttp
from dis_snek import CommandTypes, InteractionContext, context_menu

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message
from settings import COMMAND_GUILD_SCOPE

# =============
# Descend Only!
# =============


class MessageMenuCommands(BaseScale):
    """
    Add the selected image to the guild as an emoji
    """

    # todo perms
    @context_menu(name="Add Emoji", context_type=CommandTypes.MESSAGE, scopes=COMMAND_GUILD_SCOPE)
    async def add_emoji(self, ctx: InteractionContext):
        message = await ctx.channel.get_message(ctx.target_id)

        if not (message.attachments or len(message.attachments) > 1):
            await ctx.send(
                ephemeral=True,
                embeds=embed_message("Error", "There either is no image in that message, or more than one"),
            )
            return

        image = message.attachments[0]
        async with aiohttp.ClientSession() as session:
            async with session.get(image.url) as resp:
                if resp.status != 200:
                    await ctx.send(ephemeral=True, embeds=embed_message("Error", "Web request failed, try again"))
                image_data = io.BytesIO(await resp.read())

        # todo wait for modals
        name = "aaa"

        emoji = await ctx.guild.create_custom_emoji(name=name, imagefile=image_data)
        await message.add_reaction(emoji)
        await ctx.send("Success!", ephemeral=True)


def setup(client):
    MessageMenuCommands(client)
