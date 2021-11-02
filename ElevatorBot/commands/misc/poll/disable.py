from dis_snek.models import InteractionContext, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.subCommandTemplates import poll_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.poll import Poll


class PollDisable(BaseScale):
    @slash_command(
        **poll_sub_command,
        sub_cmd_name="disable",
        sub_cmd_description="Disable a poll",
    )
    @slash_option(
        name="poll_id", description="The ID of the poll", opt_type=OptionTypes.INTEGER, required=True, min_value=0
    )
    async def _poll_disable(self, ctx: InteractionContext, poll_id: int):
        poll = await Poll.from_poll_id(poll_id=poll_id, ctx=ctx)

        if poll:
            await poll.disable(ctx=ctx)


def setup(client):
    PollDisable(client)
