from dis_snek.models import InteractionContext, OptionTypes, slash_option, sub_command

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.poll import Poll


class PollAdd(BaseScale):
    @sub_command(
        base_name="poll",
        base_description="Making polls easy",
        sub_name="add",
        sub_description="Add an option to a poll",
    )
    @slash_option(
        name="poll_id",
        description="The ID of the poll",
        opt_type=OptionTypes.INTEGER,
        required=True,
    )
    @slash_option(
        name="option",
        description="The name the option should have",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def _poll_add(self, ctx: InteractionContext, poll_id: int, option: str):
        poll = await Poll.from_poll_id(poll_id=poll_id, ctx=ctx)

        if poll:
            await poll.add_new_option(ctx=ctx, option=option)


def setup(client):
    PollAdd(client)
