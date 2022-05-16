from naff import slash_command

from ElevatorBot.commandHelpers.subCommandTemplates import roles_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.destiny.roles import Roles
from ElevatorBot.discordEvents.base import ElevatorInteractionContext


class RoleGet(BaseModule):
    @slash_command(
        **roles_sub_command,
        sub_cmd_name="get",
        sub_cmd_description="Assigns you all the Destiny 2 achievement roles you have earned",
    )
    async def get(self, ctx: ElevatorInteractionContext):
        # get new roles and update the member
        roles = Roles(ctx=ctx, guild=ctx.guild, member=ctx.author)
        await roles.update()


def setup(client):
    RoleGet(client)
