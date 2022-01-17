from dis_snek.models import InteractionContext, Member, slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message


class IdGet(BaseScale):
    """
    Get a users Bungie Name. It can be used to join people in Destiny 2 without adding them as a friend
    """

    @slash_command(
        name="id",
        description="Get a users Bungie Name. It can be used to join people in Destiny 2",
    )
    @default_user_option()
    async def id(self, ctx: InteractionContext, user: Member = None):
        member = user or ctx.author

        destiny_profile = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)
        result = await destiny_profile.get_destiny_name()

        if not result:
            return
        else:
            await ctx.send(
                embeds=embed_message(
                    f"{member.display_name}'s Join Code",
                    f"`/join {result.name}`",
                ),
            )


def setup(client):
    IdGet(client)
