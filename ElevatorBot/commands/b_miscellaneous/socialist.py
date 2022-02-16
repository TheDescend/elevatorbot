from dis_snek import InteractionContext, slash_command

from ElevatorBot.commands.base import BaseScale
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class Socialist(BaseScale):

    # todo perms
    @slash_command(name="socialist", description="Spams `#socialist` 🙃", scopes=get_setting("COMMAND_GUILD_SCOPE"))
    async def socialist(self, ctx: InteractionContext):
        """Spams #socialist"""

        await ctx.send("No 🙃")


def setup(client):
    Socialist(client)
