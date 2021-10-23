from dis_snek.models import InteractionContext, OptionTypes, slash_option, sub_command

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.poll import Poll


class PollDisable(BaseScale):
    @sub_command(
        base_name="poll",
        base_description="Making polls easy",
        sub_name="disable",
        sub_description="Disable a poll",
    )
    @slash_option(
        name="poll_id",
        description="The ID of the poll",
        opt_type=OptionTypes.INTEGER,
        required=True,
    )
    async def _poll_disable(self, ctx: InteractionContext, poll_id: int):
        poll = await Poll.from_poll_id(poll_id=poll_id, ctx=ctx)

        if poll:
            await poll.disable(ctx=ctx)


def setup(client):
    PollDisable(client)
