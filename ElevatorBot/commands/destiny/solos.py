import asyncio
from typing import Optional

from dis_snek import ActionRow, Button, ButtonStyles, ComponentContext, Message
from dis_snek.models import InteractionContext, Member, slash_command
from dis_snek.models.events import Component

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message
from NetworkingSchemas.destiny.account import DestinyLowMansModel


class Solos(BaseScale):
    @slash_command(
        name="solos", description="Shows you an overview of your notable Destiny 2 solo activity completions"
    )
    @default_user_option()
    async def solos(self, ctx: InteractionContext, user: Member = None):
        member = user or ctx.author
        account = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)

        # get the solo data
        solos = await account.get_solos()
        data = {solo.category: solo.solos for solo in solos.categories}

        # display the data using the first category as a key
        await self.display_solo_page(ctx=ctx, member=member, data=data, key=list(data)[0])

    async def display_solo_page(
        self,
        ctx: InteractionContext,
        member: Member,
        data: dict[str:DestinyLowMansModel],
        key: str,
        button_ctx: Optional[ComponentContext] = None,
        message: Optional[Message] = None,
    ):
        """Displays the different pages of the command with an option to switch"""

        relevant_solos = data[key]

        # start building the return embed
        embed = embed_message(f"{member.display_name}'s Destiny Solos")

        # add the fields
        for solo_data in relevant_solos.solos:
            embed.add_field(
                name=solo_data.activity_name,
                value=f"""Solo Completions: **{solo_data.count}**\nSolo Flawless Count: **{solo_data.flawless_count}**\nFastest Solo: **{solo_data.fastest}**""",
                inline=True,
            )

        # add a pity description
        if not relevant_solos.solos:
            embed.description = "You do not seem to have any notable solo completions"

        # send or edit message
        if not button_ctx:
            components = [
                ActionRow(
                    *[
                        Button(
                            custom_id=f"solos|{category}",
                            style=ButtonStyles.GREEN,
                            label=category,
                        )
                        for category in data
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
            await button_ctx.edit_origin(components=None)
            return
        else:
            # display the new data
            await self.display_solo_page(
                ctx=ctx,
                member=member,
                data=data,
                key=component.context.custom_id.split("|")[1],
                button_ctx=component.context,
                message=message,
            )


def setup(client):
    Solos(client)
