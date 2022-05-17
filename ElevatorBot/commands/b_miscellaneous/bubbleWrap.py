import asyncio

from naff import ActionRow, Button, ButtonStyles, Message, slash_command
from naff.api.events import Component

from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message


class BubbleWrap(BaseModule):
    @slash_command(
        name="bubble_wrap",
        description="This 100% recreates the happy feeling of popping bubble wrap",
        dm_permission=False,
    )
    async def bubble_wrap(self, ctx: ElevatorInteractionContext):
        components = [
            ActionRow(
                *[
                    Button(
                        label="⁣",
                        custom_id=f"{j}|{i}",
                        style=ButtonStyles.GREEN,
                    )
                    for i in range(5)
                ]
            )
            for j in range(5)
        ]

        message = await ctx.send(embeds=embed_message("Pop It Like You Mean It"), components=components)

        # wait for pops
        await self.wait_for_pops(components=components, message=message)

    async def wait_for_pops(self, components: list[ActionRow], message: Message):
        """Wait for people to pop the bubble wrap"""

        # pop them
        try:
            component: Component = await self.bot.wait_for_component(components=components, timeout=60)
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
            obj.label = "pop"

            await component.context.edit_origin(components=components)

            # wait again
            await self.wait_for_pops(components=components, message=message)


def setup(client):
    BubbleWrap(client)
