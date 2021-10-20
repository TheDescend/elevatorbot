from dis_snek.models import InteractionContext
from dis_snek.models import Member
from dis_snek.models import sub_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.roles import Roles


class RoleOverview(BaseScale):
    @sub_command(
        base_name="roles",
        base_description="Various commands concerning Destiny 2 achievement discord roles",
        sub_name="overview",
        sub_description="Shows you what roles you can still achieve in this clan",
    )
    @default_user_option()
    async def _roles_overview(self, ctx: InteractionContext, user: Member = None):
        # might take a sec
        await ctx.defer()

        # get the role overview and send that
        roles = Roles(client=self.client, guild=ctx.guild, member=user or ctx.author)
        await roles.overview(ctx=ctx)


def setup(client):
    RoleOverview(client)
