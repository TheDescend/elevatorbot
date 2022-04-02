import json
from typing import Optional

from dis_snek import ComponentContext, InteractionContext, Member, Message, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.paginator import paginate
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import capitalize_string, embed_message, format_progress, un_capitalize_string
from ElevatorBot.networking.destiny.account import DestinyAccount
from Shared.networkingSchemas.destiny import DestinyCraftableModel


class Craftables(BaseScale):
    @slash_command(
        name="craftables",
        description="View your craftables",
    )
    @default_user_option()
    async def seals(self, ctx: InteractionContext, user: Member = None):
        member = user or ctx.author

        destiny_profile = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)
        result = await destiny_profile.get_craftables()

        # display the data using the first category as a key
        await self.display_craftable_page(
            ctx=ctx,
            member=member,
            key=capitalize_string(list(result.dict())[0]),
            data=result,
        )

    async def display_seals_page(
        self,
        ctx: InteractionContext,
        member: Member,
        data: list[DestinyCraftableModel],
        key: str,
        button_ctx: Optional[ComponentContext] = None,
        message: Optional[Message] = None,
    ):
        """Displays the different pages of the command with an option to switch"""

        # # sort the seals by percent done
        # sorted_seals = sorted(
        #     getattr(data, un_capitalize_string(key)), key=lambda seal: seal.completion_percentage, reverse=True
        # )

        # format the message nicely
        embed = embed_message(
            f"{key} Craftable",
            "\n".join([json.dumps(craftable) for craftable in data]),
            member=member,
        )

        # paginate that
        await paginate(
            ctx=ctx,
            member=member,
            embed=embed,
            current_category=key,
            categories=[
                capitalize_string(category) for category, data in data.dict().items() if isinstance(data, list)
            ],
            callback=self.display_seals_page,
            callback_data=data,
            button_ctx=button_ctx,
            message=message,
        )


def setup(client):
    Craftables(client)
