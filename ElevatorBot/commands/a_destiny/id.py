from naff import Member, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.account import DestinyAccount


class IdGet(BaseModule):
    """
    Get a users Bungie Name. It can be used to join people in Destiny 2 without adding them as a friend
    """

    @slash_command(
        name="id",
        description="Get a users Bungie Name. It can be used to join people in Destiny 2",
        dm_permission=False,
    )
    @default_user_option()
    async def id(self, ctx: ElevatorInteractionContext, user: Member = None):
        member = user or ctx.author

        destiny_profile = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)
        result = await destiny_profile.get_destiny_name()

        if not result:
            return
        else:
            await ctx.send(
                embeds=embed_message(f"Join Code", f"`/join {result.name}`", member=member),
            )


def setup(client):
    IdGet(client)
