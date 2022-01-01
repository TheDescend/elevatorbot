from dis_snek.models import InteractionContext, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.subCommandTemplates import poll_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.poll import Poll


class PollAdd(BaseScale):
    @slash_command(
        **poll_sub_command,
        sub_cmd_name="add",
        sub_cmd_description="Add an option to an existing poll",
    )
    @slash_option(
        name="poll_id", description="The ID of the poll", opt_type=OptionTypes.INTEGER, required=True, min_value=0
    )
    @slash_option(
        name="option",
        description="The name the option should have",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def add(self, ctx: InteractionContext, poll_id: int, option: str):
        poll = await Poll.from_poll_id(poll_id=poll_id, ctx=ctx)

        if poll:
            await poll.add_new_option(ctx=ctx, option=option)


def setup(client):
    PollAdd(client)
