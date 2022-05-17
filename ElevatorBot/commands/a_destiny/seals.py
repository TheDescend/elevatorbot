from typing import Optional

from naff import Member, Message, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.paginator import paginate
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorComponentContext, ElevatorInteractionContext
from ElevatorBot.misc.formatting import capitalize_string, embed_message, format_progress, un_capitalize_string
from ElevatorBot.networking.destiny.account import DestinyAccount
from Shared.networkingSchemas.destiny import DestinySealsModel


class Seals(BaseModule):
    @slash_command(
        name="seals",
        description="View all Destiny 2 seals and your completion status",
        dm_permission=False,
    )
    @default_user_option()
    async def seals(self, ctx: ElevatorInteractionContext, user: Member = None):
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
        ctx: ElevatorInteractionContext,
        member: Member,
        data: DestinySealsModel,
        key: str,
        button_ctx: Optional[ElevatorComponentContext] = None,
        message: Optional[Message] = None,
    ):
        """Displays the different pages of the command with an option to switch"""

        # sort the seals by percent done
        sorted_seals = sorted(
            getattr(data, un_capitalize_string(key)), key=lambda seal: seal.completion_percentage, reverse=True
        )

        # format the message nicely
        embed = embed_message(
            f"{key} Seals",
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
    Seals(client)
