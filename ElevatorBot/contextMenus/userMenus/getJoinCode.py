from dis_snek.models import CommandTypes
from dis_snek.models import context_menu
from dis_snek.models import InteractionContext

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message


class UserMenuCommands(BaseScale):
    """
    Gets collected info for the specified user
    """

    @context_menu(name="Get Join Code", context_type=CommandTypes.USER)
    async def command(self, ctx: InteractionContext):
        member = await ctx.guild.get_member(ctx.target_id)

        destiny_profile = DestinyAccount(client=ctx.bot, discord_member=member, discord_guild=ctx.guild)
        result = await destiny_profile.get_destiny_name()

        if not result:
            await result.send_error_message(ctx, hidden=True)
        else:
            await ctx.send(
                ephemeral=True,
                embeds=embed_message(
                    f"{member.display_name}'s Join Code",
                    f"`/join {result.result['name']}`",
                ),
            )


def setup(client):
    UserMenuCommands(client)
