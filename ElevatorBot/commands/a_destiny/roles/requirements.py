from dis_snek import InteractionContext, Member, OptionTypes, Role, slash_command, slash_option

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.subCommandTemplates import roles_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.roles import Roles


class RoleRequirements(BaseScale):
    @slash_command(
        **roles_sub_command,
        sub_cmd_name="requirements",
        sub_cmd_description="Shows you what you still need to do to get the specified Destiny 2 achievement role",
    )
    @slash_option(name="role", description="The role you want to look up", opt_type=OptionTypes.ROLE, required=True)
    @default_user_option()
    async def requirements(self, ctx: InteractionContext, role: Role, user: Member = None):
        # get role get_requirements
        roles = Roles(ctx=ctx, guild=ctx.guild, member=user or ctx.author)
        await roles.get_requirements(role=role)


def setup(client):
    RoleRequirements(client)
