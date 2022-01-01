import asyncio

from dis_snek.models import (
    ActionRow,
    Button,
    ButtonStyles,
    InteractionContext,
    slash_command,
)
from dis_snek.models.events import Component

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message


class BubbleWrap(BaseScale):
    @slash_command(name="bubble_wrap", description="This 100% recreates the happy feeling of popping bubble wrap")
    async def bubble_wrap(self, ctx: InteractionContext):
        components = [
            ActionRow(
                *[
                    Button(
                        custom_id=f"{j}|{i}",
                        style=ButtonStyles.GREEN,
                    )
                    for i in range(5)
                ]
            )
            for j in range(5)
        ]

        message = await ctx.send(embeds=embed_message("Pop It Like You Mean It"), components=components)

        # pop them
        try:
            component: Component = await ctx.bot.wait_for_component(components=components, timeout=60)
        except asyncio.TimeoutError:
            # disable all buttons
            for row in components:
                for button in row.components:
                    button.disabled = True
            await message.edit(components=components)
        else:
            # find the pressed button and disable it
            j, i = component.context.custom_id.split("|")
            obj = components[int(j)].components[int(i)]
            obj.disabled = True
            obj.label = "_pop_"

            await component.context.edit_origin(components=components)


def setup(client):
    BubbleWrap(client)
