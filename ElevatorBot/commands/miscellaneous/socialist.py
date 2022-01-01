from dis_snek.models import InteractionContext, slash_command

from ElevatorBot.commands.base import BaseScale
from settings import COMMAND_GUILD_SCOPE

# =============
# Descend Only!
# =============


class Socialist(BaseScale):

    # todo perms
    @slash_command(name="socialist", description="Spams `#socialist` 🙃", scopes=COMMAND_GUILD_SCOPE)
    async def socialist(self, ctx: InteractionContext):
        """Spams #socialist"""

        await ctx.send("No 🙃")


def setup(client):
    Socialist(client)
