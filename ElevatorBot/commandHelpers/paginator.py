import asyncio
from copy import copy
from typing import Any, Callable, Coroutine, Optional

from naff import ActionRow, Button, ButtonStyles, Embed, Member, Message
from naff.api.events import Component

from ElevatorBot.discordEvents.base import ElevatorComponentContext, ElevatorInteractionContext


async def paginate(
    ctx: ElevatorInteractionContext,
    member: Member,
    embed: Embed,
    current_category: str,
    categories: list[str],
    callback: Callable[..., Coroutine],
    callback_data: Any,
    button_ctx: Optional[ElevatorComponentContext] = None,
    message: Optional[Message] = None,
):
    """Paginate the command by key"""

    components = [
        ActionRow(
            *[
                Button(
                    custom_id=f"paginator|{member.id}|{category}",
                    style=ButtonStyles.GREEN,
                    label=category,
                    disabled=category == current_category,
                )
                for category in categories
            ]
        ),
    ]

    # send or edit message
    if not button_ctx:
        message = await ctx.send(embeds=embed, components=components)
    else:
        await button_ctx.edit_origin(embeds=embed, components=components)

    # wait for a button press for 60s
    def check(component_check: Component):
        return component_check.context.author == ctx.author

    try:
        component = await ctx.bot.wait_for_component(
            messages=message,
            timeout=60,
            check=check,
        )
    except asyncio.TimeoutError:
        # disable all buttons
        new_components = copy(message.components)
        for button in new_components[0].components:
            button.disabled = True

        await message.edit(components=new_components)
        return
    else:
        # display the new data
        await callback(
            ctx=ctx,
            member=member,
            key=component.context.custom_id.split("|")[2],
            button_ctx=component.context,
            message=message,
            data=callback_data,
        )
