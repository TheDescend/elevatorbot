from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.core.destiny.clan import DestinyClan
from ElevatorBot.misc.formating import embed_message


class ClanUnlink(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="clan",
        base_description="Everything concerning the link from this discord guild to your Destiny 2 clan",
        name="unlink",
        description="Unlink the current Destiny 2 clan with this discord. Requires Admin in both Discord",
        base_default_permission=False,
        base_permissions=permissions_admin,
    )
    async def _unlink(
        self,
        ctx: SlashContext,
    ):
        """Unlink the current Destiny 2 clan with this discord. Requires Admin in both Discord"""

        clan = DestinyClan(client=ctx.bot, discord_member=ctx.author, discord_guild=ctx.guild)
        result = await clan.unlink()

        if not result:
            await result.send_error_message(ctx)
        else:
            await ctx.send(
                embed=embed_message(
                    "Success",
                    f"This discord server has been successfully unlinked from the clan `{result.result['clan_name']}`"
                )
            )


def setup(client):
    client.add_cog(ClanUnlink(client))
