from naff import Extension, slash_command

from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.profile import DestinyProfile


class UnRegister(Extension):
    def __init__(self, client):
        self.client = client

    @slash_command(name="unregister", description="Unlink your Destiny 2 account from ElevatorBot")
    async def unregister(
        self,
        ctx: ElevatorInteractionContext,
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
