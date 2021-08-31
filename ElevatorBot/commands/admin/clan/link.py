from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.commandHelpers.permissionTemplates import permissions_admin
from ElevatorBot.core.destiny.clan import DestinyClan
from ElevatorBot.misc.formating import embed_message


class ClanLink(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="clan",
        base_description="Everything concerning the link from this discord guild to your Destiny 2 clan",
        name="link",
        description="Links your own Destiny 2 clan with this discord. Requires Admin in both Discord and Destiny",
        base_default_permission=False,
        base_permissions=permissions_admin,
    )
    async def _link(
        self,
        ctx: SlashContext,
    ):
        """Links your own Destiny 2 clan with this discord. Requires Admin in both Discord and Destiny"""

        clan = DestinyClan(client=ctx.bot, discord_member=ctx.author, discord_guild=ctx.guild)
        result = await clan.link()

        if not result:
            await result.send_error_message(ctx)
        else:
            await ctx.send(
                embed=embed_message(
                    "Success",
                    f"This discord server has been successfully linked to the clan `{result.result['clan_name']}`",
                )
            )


def setup(client):
    client.add_cog(ClanLink(client))
