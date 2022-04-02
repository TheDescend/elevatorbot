import asyncio
import io
import re

import aiohttp
from dis_snek import CommandTypes, InteractionContext, Message, Modal, ShortText, context_menu

from ElevatorBot.commandHelpers.responseTemplates import respond_timeout
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class EmojiCommands(BaseScale):
    """
    Add the selected image to the guild as an emoji
    """

    # todo perms
    @context_menu(name="Add Emoji", context_type=CommandTypes.MESSAGE, scopes=get_setting("COMMAND_GUILD_SCOPE"))
    async def add_emoji(self, ctx: InteractionContext):
        if ctx.author.id not in [238388130581839872, 206878830017773568]:
            await ctx.send(
                "This is blocked for now, since it it waiting for a vital unreleased discord feature", ephemeral=True
            )
            return

        message: Message = ctx.target

        # attachments
        if message.attachments and len(message.attachments) == 1:
            url = message.attachments[0].url

        # url
        elif url := re.search(r"([a-z\-_0-9\/\:\.]*\.(jpg|jpeg|png|gif))", message.content):
            pass

        else:
            await ctx.send(
                ephemeral=True,
                embeds=embed_message("Error", "There either is no image in that message, or more than one"),
            )
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send(ephemeral=True, embeds=embed_message("Error", "Web request failed, try again"))
                image_data = io.BytesIO(await resp.read())

        # ask for name in a modal
        modal = Modal(
            title="Emoji Name",
            components=[
                ShortText(
                    label="What should the name of the emoji be?",
                    custom_id="name",
                    placeholder="Required",
                    min_length=1,
                    max_length=20,
                    required=True,
                ),
            ],
        )
        await ctx.send_modal(modal=modal)

        # wait 5 minutes for them to fill it out
        try:
            modal_ctx = await ctx.bot.wait_for_modal(modal=modal, timeout=300)

        except asyncio.TimeoutError:
            # give timeout message
            await respond_timeout(ctx=ctx)
            return

        else:
            await modal_ctx.defer()
            emoji = await ctx.guild.create_custom_emoji(name=modal_ctx.responses["name"], imagefile=image_data)
            await message.add_reaction(emoji)
            await modal_ctx.send("Success!", ephemeral=True)


def setup(client):
    EmojiCommands(client)
