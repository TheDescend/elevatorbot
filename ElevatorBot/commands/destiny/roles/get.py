from dis_snek.models import InteractionContext, slash_command

from ElevatorBot.commandHelpers.subCommandTemplates import roles_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.roles import Roles


class RoleGet(BaseScale):
    @slash_command(
        **roles_sub_command,
        sub_cmd_name="get",
        sub_cmd_description="Assigns you all the roles you've earned",
    )
    async def _roles_get(self, ctx: InteractionContext):
        # might take a sec
        await ctx.defer()

        # get new roles and update the member
        roles = Roles(client=self.client, guild=ctx.guild, member=ctx.author)
        await roles.update(ctx=ctx)


def setup(client):
    RoleGet(client)
