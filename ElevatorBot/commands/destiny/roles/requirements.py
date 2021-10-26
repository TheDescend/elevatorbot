from dis_snek.models import (
    InteractionContext,
    Member,
    OptionTypes,
    Role,
    slash_command,
    slash_option,
)

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.subCommandTemplates import roles_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.roles import Roles


class RoleRequirements(BaseScale):
    @slash_command(
        **roles_sub_command,
        sub_cmd_name="get_requirements",
        sub_cmd_description="Shows you what you need to do to get the specified role",
    )
    @slash_option(
        name="role", description="The name of the role you want to look up", opt_type=OptionTypes.ROLE, required=True
    )
    @default_user_option()
    async def _roles_requirements(self, ctx: InteractionContext, role: Role, user: Member = None):
        # might take a sec
        await ctx.defer()

        # get role get_requirements
        roles = Roles(client=self.client, guild=ctx.guild, member=user or ctx.author)
        await roles.get_requirements(role=role, ctx=ctx)


def setup(client):
    RoleRequirements(client)
