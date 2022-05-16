from naff import CommandTypes, Member, context_menu

from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.base import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.account import DestinyAccount


class UserMenuCommands(BaseModule):
    """
    Gets the selected users Destiny 2 join code, like `/join Name#1234`
    """

    @context_menu(name="Get Join Code", context_type=CommandTypes.USER)
    async def command(self, ctx: ElevatorInteractionContext):
        member: Member = ctx.target

        destiny_profile = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)
        destiny_profile.hidden = True
        result = await destiny_profile.get_destiny_name()

        await ctx.send(
            ephemeral=True,
            embeds=embed_message(
                f"{member.display_name}'s Join Code",
                f"`/join {result.name}`",
            ),
        )


def setup(client):
    UserMenuCommands(client)
