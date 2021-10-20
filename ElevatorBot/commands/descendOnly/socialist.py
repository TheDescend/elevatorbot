from dis_snek.models import InteractionContext
from dis_snek.models import slash_command


from ElevatorBot.commands.base import BaseScale


class Socialist(BaseScale):

    # todo perms
    @slash_command(name="socialist", description="Spams #socialist")
    async def _socialist(self, ctx: InteractionContext):
        """Spams #socialist"""

        await ctx.send("No 🙃")


def setup(client):
    Socialist(client)
