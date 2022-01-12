from typing import Optional

from dis_snek import ComponentContext, Message
from dis_snek.models import InteractionContext, Member, slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.paginator import paginate
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import capitalize_string, embed_message, format_progress, un_capitalize_string
from Shared.NetworkingSchemas.destiny import DestinySealsModel


class Seals(BaseScale):
    @slash_command(
        name="seals",
        description="View all Destiny 2 seals and your completion status",
    )
    @default_user_option()
    async def seals(self, ctx: InteractionContext, user: Member = None):
        member = user or ctx.author

        destiny_profile = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)
        result = await destiny_profile.get_seal_completion()

        # display the data using the first category as a key
        await self.display_seals_page(
            ctx=ctx,
            member=member,
            key=capitalize_string(list(result.dict())[0]),
            data=result,
        )

    async def display_seals_page(
        self,
        ctx: InteractionContext,
        member: Member,
        data: DestinySealsModel,
        key: str,
        button_ctx: Optional[ComponentContext] = None,
        message: Optional[Message] = None,
    ):
        """Displays the different pages of the command with an option to switch"""

        # sort the seals by percent done
        sorted_seals = sorted(
            getattr(data, un_capitalize_string(key)), key=lambda seal: seal.completion_percentage, reverse=True
        )

        # format the message nicely
        embed = embed_message(
            f"{member.display_name}'s {key} Seals",
            "\n".join(
                [
                    format_progress(
                        name=seal.name,
                        completion_status=seal.completion_status,
                        completion_percentage=seal.completion_percentage,
                    )
                    for seal in sorted_seals
                ]
            ),
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
    Seals(client)
