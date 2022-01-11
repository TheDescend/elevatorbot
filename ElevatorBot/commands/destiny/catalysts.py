from typing import Optional

from dis_snek import ComponentContext, Message
from dis_snek.models import InteractionContext, Member, slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.paginator import paginate
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message, format_progress
from Shared.NetworkingSchemas.destiny import DestinyCatalystsModel


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
        await self.display_catalyst_page(
            ctx=ctx, member=member, data=catalysts, key=list(catalysts.dict())[0].capitalize()
        )

    async def display_catalyst_page(
        self,
        ctx: InteractionContext,
        member: Member,
        data: DestinyCatalystsModel,
        key: str,
        button_ctx: Optional[ComponentContext] = None,
        message: Optional[Message] = None,
    ):
        """Displays the different pages of the command with an option to switch"""

        # sort the catalysts by len
        sorted_catalyst = sorted(
            getattr(data, key.lower()), key=lambda catalyst: catalyst.completion_percentage, reverse=True
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

        # paginate that
        await paginate(
            ctx=ctx,
            member=member,
            embed=embed,
            current_category=key,
            categories=[category.capitalize() for category, data in data.dict().items() if isinstance(data, list)],
            callback=self.display_catalyst_page,
            callback_data=data,
            button_ctx=button_ctx,
            message=message,
        )


def setup(client):
    Catalysts(client)
