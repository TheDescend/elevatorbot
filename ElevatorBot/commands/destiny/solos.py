from typing import Optional

from dis_snek import ComponentContext, Message
from dis_snek.models import InteractionContext, Member, slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.paginator import paginate
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message, format_timedelta
from Shared.NetworkingSchemas.destiny import DestinyLowMansModel


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
        embed = embed_message(f"{member.display_name}'s Solos - {key}")

        # add the fields
        for solo_data in relevant_solos:
            embed.add_field(
                name=solo_data.activity_name,
                value=f"""Solo Completions: **{solo_data.count}**\nSolo Flawless Count: **{solo_data.flawless_count}**\nFastest Solo: **{format_timedelta(solo_data.fastest)}**""",
                inline=True,
            )

        # add a pity description
        if not relevant_solos:
            embed.description = "You do not seem to have any notable solo completions"

        # paginate that
        await paginate(
            ctx=ctx,
            member=member,
            embed=embed,
            current_category=key,
            categories=list(data),
            callback=self.display_solo_page,
            callback_data=data,
            button_ctx=button_ctx,
            message=message,
        )


def setup(client):
    Solos(client)
