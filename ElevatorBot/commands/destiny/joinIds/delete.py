from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.core.destiny.profile import DestinyProfile
from ElevatorBot.misc.formating import embed_message


class IdDelete(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="id",
        base_description="Steam IDs which can be used to join people in Destiny 2 without adding them as a friend",
        name="delete",
        description="Delete your linked Steam ID",
    )
    async def _delete(self, ctx: SlashContext):
        """Delete your linked Steam ID"""

        destiny_profile = DestinyProfile(client=ctx.bot, discord_member=ctx.author, discord_guild=ctx.guild)
        result = await destiny_profile.delete_join_id()

        if not result:
            await result.send_error_message(ctx, hidden=True)
        else:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    f"Success",
                    f"Your Join Code has been deleted",
                ),
            )


def setup(client):
    client.add_cog(IdDelete(client))
