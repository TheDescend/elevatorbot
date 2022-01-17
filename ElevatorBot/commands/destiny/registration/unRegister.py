from dis_snek.models import InteractionContext, Scale, slash_command

from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.misc.formatting import embed_message


class UnRegister(Scale):
    def __init__(self, client):
        self.client = client

    @slash_command(name="unregister", description="Unlink your Destiny 2 account from ElevatorBot")
    async def unregister(
        self,
        ctx: InteractionContext,
    ):
        """Unlink your Destiny 2 account from ElevatorBot"""

        destiny_profile = DestinyProfile(ctx=ctx, discord_member=ctx.author, discord_guild=ctx.guild)
        await destiny_profile.delete()

        await ctx.send(
            embeds=embed_message(
                "See Ya",
                "There was a flash and suddenly I do not remember anything about you anymore",
            ),
            ephemeral=True,
        )


def setup(client):
    UnRegister(client)
