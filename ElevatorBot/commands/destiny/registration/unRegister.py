from discord.ext.commands import Cog
from discord_slash import cog_ext
from discord_slash import SlashContext

from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.misc.formating import embed_message


class UnRegister(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="unregister",
        description="Unlink your Destiny 2 account from ElevatorBot",
    )
    async def _unregister(
        self,
        ctx: SlashContext,
    ):
        """Unlink your Destiny 2 account from ElevatorBot"""

        destiny_profile = DestinyProfile(client=ctx.bot, discord_member=ctx.author, discord_guild=ctx.guild)
        result = await destiny_profile.delete()

        if not result:
            await result.send_error_message(ctx, hidden=True)
        else:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "See Ya",
                    "There was a flash and suddenly I do not remember anything about you anymore",
                ),
            )


def setup(client):
    client.add_cog(UnRegister(client))
