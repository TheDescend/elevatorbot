from naff import Member, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.subCommandTemplates import roles_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.destiny.roles import Roles
from ElevatorBot.discordEvents.base import ElevatorInteractionContext


class RoleMissing(BaseModule):
    @slash_command(
        **roles_sub_command,
        sub_cmd_name="missing",
        sub_cmd_description="Shows you what Destiny 2 achievement roles you can still achieve",
    )
    @default_user_option()
    async def missing(self, ctx: ElevatorInteractionContext, user: Member = None):

        # get the roles missing and send that
        roles = Roles(ctx=ctx, guild=ctx.guild, member=user or ctx.author)
        await roles.get_missing()


def setup(client):
    RoleMissing(client)
