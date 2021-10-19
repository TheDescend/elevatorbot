from dis_snek.models import InteractionContext
from dis_snek.models import slash_command

from ElevatorBot.commandHelpers.optionTemplates import misc_group
from ElevatorBot.commandHelpers.permissionTemplates import permissions_socialist
from ElevatorBot.commands.base import BaseScale


class Socialist(BaseScale):

    # todo perms
    @slash_command(name="socialist", description="Spams #socialist", **misc_group)
    async def _socialist(self, ctx: InteractionContext):
        """Spams #socialist"""

        await ctx.send("No 🙃")


def setup(client):
    Socialist(client)
