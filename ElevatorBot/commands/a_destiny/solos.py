from typing import Optional

from naff import Member, Message, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.paginator import paginate
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorComponentContext, ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message, format_timedelta
from ElevatorBot.networking.destiny.account import DestinyAccount
from Shared.networkingSchemas import DestinyUpdatedLowManModel


class Solos(BaseModule):
    @slash_command(
        name="solos", description="Shows you an overview of your notable Destiny 2 solo activity completions"
    )
    @default_user_option()
    async def solos(self, ctx: ElevatorInteractionContext, user: Member = None):
        member = user or ctx.author
        account = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)

        # get the solo data
        solos = await account.get_solos()
        data = {solo.category: solo.solos for solo in solos.categories}

        # display the data using the first category as a key
        await self.display_solo_page(ctx=ctx, member=member, data=data, key=list(data)[0])

    async def display_solo_page(
        self,
        ctx: ElevatorInteractionContext,
        member: Member,
        data: dict[str, list[DestinyUpdatedLowManModel]],
        key: str,
        button_ctx: Optional[ElevatorComponentContext] = None,
        message: Optional[Message] = None,
    ):
        """Displays the different pages of the command with an option to switch"""

        relevant_solos = data[key]

        # start building the return embed
        embed = embed_message(f"Solos - {key}", member=member)

        # add the fields
        for solo_data in relevant_solos:
            embed.add_field(
                name=solo_data.activity_name,
                value=f"""Solo Completions: **{solo_data.count}**\nSolo Flawless Count: **{solo_data.flawless_count}**\nFastest Solo: {f"[{format_timedelta(solo_data.fastest)}](https://www.bungie.net/en/PGCR/{solo_data.fastest_instance_id})" if solo_data.fastest else "None"}""",
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
