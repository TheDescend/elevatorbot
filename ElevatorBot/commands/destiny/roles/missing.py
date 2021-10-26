from dis_snek.models import InteractionContext, Member, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.subCommandTemplates import roles_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.roles import Roles


class RoleMissing(BaseScale):
    @slash_command(
        **roles_sub_command,
        sub_cmd_name="missing",
        sub_cmd_description="Shows you what roles you can still achieve in this server",
    )
    @default_user_option()
    async def _roles_missing(self, ctx: InteractionContext, user: Member = None):
        # might take a sec
        await ctx.defer()

        # get the roles missing and send that
        roles = Roles(client=self.client, guild=ctx.guild, member=user or ctx.author)
        await roles.get_missing(ctx=ctx)


def setup(client):
    RoleMissing(client)
