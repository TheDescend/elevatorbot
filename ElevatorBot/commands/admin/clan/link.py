from dis_snek.models import InteractionContext
from dis_snek.models import sub_command

from ElevatorBot.backendNetworking.destiny.clan import DestinyClan
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message


class ClanLink(BaseScale):
    """Links your own Destiny 2 clan with the discord server this was executed in"""

    # todo perms
    @sub_command(
        base_name="clan",
        base_description="Everything concerning the link from this discord guild to your Destiny 2 clan",
        sub_name="link",
        sub_description="Links your own Destiny 2 clan with this discord. Requires Admin in both Discord and Destiny",
    )
    async def _link(self, ctx: InteractionContext):

        clan = DestinyClan(client=ctx.bot, discord_member=ctx.author, discord_guild=ctx.guild)
        result = await clan.link()

        if not result:
            await result.send_error_message(ctx)
        else:
            await ctx.send(
                embeds=embed_message(
                    "Success",
                    f"This discord server has been successfully linked to the clan `{result.result['clan_name']}`",
                )
            )


def setup(client):
    ClanLink(client)
