import asyncio
import copy
import random
from typing import Optional

from naff import ActionRow, Button, ButtonStyles, Message, slash_command

from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.static.emojis import custom_emojis


class SimonSays(BaseModule):
    choices: dict[str, ButtonStyles] = {
        "blurple": ButtonStyles.PRIMARY,
        "grey": ButtonStyles.SECONDARY,
        "green": ButtonStyles.SUCCESS,
        "red": ButtonStyles.DANGER,
    }
    components: list[ActionRow] = [
        ActionRow(
            Button(style=choices["blurple"], label="⁣", disabled=False, custom_id="simonSays_blurple"),
            Button(style=choices["green"], label="⁣", disabled=False, custom_id="simonSays_green"),
        ),
        ActionRow(
            Button(style=choices["grey"], label="⁣", disabled=False, custom_id="simonSays_grey"),
            Button(style=choices["red"], label="⁣", disabled=False, custom_id="simonSays_red"),
        ),
    ]

    @slash_command(
        name="simon_says",
        description="The all time classic",
        dm_permission=False,
    )
    async def simon_says(self, ctx: ElevatorInteractionContext):
        await self.show_sequence(ctx=ctx)

    async def show_sequence(
        self, ctx: ElevatorInteractionContext, sequence: Optional[list[str]] = None, message: Optional[Message] = None
    ):
        if not sequence:
            sequence = []

        # generate a new entry
        sequence.append(random.choice(list(self.choices.keys())))

        # play sequence
        embed = embed_message(
            member=ctx.author, title="Simon Says Game", description="Playing Sequence...\n⁣\nStatus: **Pay Attention!**"
        )
        for entry in sequence:
            # disable all buttons but the one we want to highlight
            components = copy.deepcopy(self.components)
            for row in components:
                for item in row.components:
                    if entry not in item.custom_id:
                        item.disabled = True
                    else:
                        item.emoji = custom_emojis.elevator_logo

            if not message:
                message = await ctx.send(embeds=embed, components=components)
            else:
                await message.edit(embeds=embed, components=components)
            await asyncio.sleep(1)

        # question the user
        placeholder = "Waiting for your inputs...\n⁣\nStatus: **{got} / {to_get}**"
        embed.description = placeholder.format(got=0, to_get=len(sequence))
        await message.edit(embeds=embed, components=self.components)

        for i, entry in enumerate(sequence):
            try:
                component = await ctx.bot.wait_for_component(
                    components=self.components,
                    timeout=60,
                    check=lambda c: c.context.author == ctx.author,
                )
            except asyncio.TimeoutError:
                embed.description = f"Timed out!\n⁣\nScore: **{len(sequence) - 1}**"
                await message.edit(components=[], embeds=embed)
                return
            else:
                chosen = component.context.custom_id.split("_")[1]
                if chosen == entry:
                    embed.description = placeholder.format(got=i + 1, to_get=len(sequence))
                    await component.context.edit_origin(embeds=embed)

                else:
                    embed.description = (
                        f"Wrong! Correct would have been `{entry.capitalize()}`\n⁣\nScore: **{len(sequence) - 1}**"
                    )
                    await component.context.edit_origin(components=[], embeds=embed)
                    return

        # user has input all symbols correctly
        await self.show_sequence(ctx=ctx, message=message, sequence=sequence)


def setup(client):
    SimonSays(client)
