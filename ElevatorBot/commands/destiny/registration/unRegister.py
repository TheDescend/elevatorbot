from dis_snek.client import Snake
from dis_snek.models import InteractionContext
from dis_snek.models import Scale
from dis_snek.models import slash_command

from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.misc.formating import embed_message


class UnRegister(Scale):
    def __init__(self, client):
        self.client: Snake = client

    @slash_command(name="unregister", description="Unlink your Destiny 2 account from ElevatorBot")
    async def _unregister(
        self,
        ctx: InteractionContext,
    ):
        """Unlink your Destiny 2 account from ElevatorBot"""

        destiny_profile = DestinyProfile(client=ctx.bot, discord_member=ctx.author, discord_guild=ctx.guild)
        result = await destiny_profile.delete()

        if not result:
            await result.send_error_message(ctx, hidden=True)
        else:
            await ctx.send(
                ephemeral=True,
                embeds=embed_message(
                    "See Ya",
                    "There was a flash and suddenly I do not remember anything about you anymore",
                ),
            )


def setup(client):
    UnRegister(client)
