from dis_snek.models import InteractionContext
from dis_snek.models import Member
from dis_snek.models import OptionTypes
from dis_snek.models import Role
from dis_snek.models import slash_option
from dis_snek.models import sub_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.roles import Roles


class RoleRequirements(BaseScale):
    @sub_command(
        base_name="roles",
        base_description="Various commands concerning Destiny 2 achievement discord roles",
        sub_name="requirements",
        sub_description="Shows you what you need to do to get the specified role",
    )
    @slash_option(
        name="role", description="The name of the role you want to look up", opt_type=OptionTypes.ROLE, required=True
    )
    @default_user_option()
    async def _roles_requirements(self, ctx: InteractionContext, role: Role, user: Member = None):
        # might take a sec
        await ctx.defer()

        # get role requirements
        roles = Roles(client=self.client, guild=ctx.guild, member=user or ctx.author)
        await roles.requirements(role=role, ctx=ctx)


def setup(client):
    RoleRequirements(client)
