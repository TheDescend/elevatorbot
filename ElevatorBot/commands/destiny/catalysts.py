import asyncio
from copy import copy
from typing import Optional

from dis_snek import ActionRow, Button, ButtonStyles, ComponentContext, Message
from dis_snek.models import InteractionContext, Member, slash_command
from dis_snek.models.events import Component

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message, format_progress
from NetworkingSchemas.destiny.account import (
    DestinyCatalystModel,
    DestinyCatalystsModel,
)


class Catalysts(BaseScale):
    @slash_command(
        name="catalysts", description="Shows you Destiny 2 exotic weapon catalysts and their completion status"
    )
    @default_user_option()
    async def catalysts(self, ctx: InteractionContext, user: Member = None):
        member = user or ctx.author

        account = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)
        catalysts = await account.get_catalyst_completion()

        # display the data using the first category as a key
        await self.display_catalyst_page(ctx=ctx, member=member, catalysts=catalysts, key=list(catalysts.dict())[0])

    async def display_catalyst_page(
        self,
        ctx: InteractionContext,
        member: Member,
        catalysts: DestinyCatalystsModel,
        key: str,
        button_ctx: Optional[ComponentContext] = None,
        message: Optional[Message] = None,
    ):
        """Displays the different pages of the command with an option to switch"""

        # sort the catalysts by len
        sorted_catalyst = sorted(
            getattr(catalysts, key.lower()), key=lambda catalyst: catalyst.completion_percentage, reverse=True
        )

        # format the message
        embed = embed_message(
            f"{member.display_name}'s {key} Weapon Catalysts",
            "\n".join(
                [
                    format_progress(
                        name=catalyst.name,
                        completion_status=catalyst.completion_status,
                        completion_percentage=catalyst.completion_percentage,
                    )
                    for catalyst in sorted_catalyst
                ]
            ),
        )

        # send or edit message
        if not button_ctx:
            components = [
                ActionRow(
                    *[
                        Button(
                            custom_id=f"catalysts|{category.capitalize()}",
                            style=ButtonStyles.GREEN,
                            label=category.capitalize(),
                        )
                        for category, data in catalysts.dict().items()
                        if isinstance(data, list)
                    ]
                ),
            ]

            message = await ctx.send(embeds=embed, components=components)
        else:
            await button_ctx.edit_origin(embeds=embed)

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
            await self.display_catalyst_page(
                ctx=ctx,
                member=member,
                catalysts=catalysts,
                key=component.context.custom_id.split("|")[1],
                button_ctx=component.context,
                message=message,
            )


def setup(client):
    Catalysts(client)
