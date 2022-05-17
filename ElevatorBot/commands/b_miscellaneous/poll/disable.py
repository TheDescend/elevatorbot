from naff import OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.subCommandTemplates import poll_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.poll import Poll
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext


class PollDisable(BaseModule):
    @slash_command(
        **poll_sub_command,
        sub_cmd_name="disable",
        sub_cmd_description="Disable an existing poll",
        dm_permission=False,
    )
    @slash_option(
        name="poll_id", description="The ID of the poll", opt_type=OptionTypes.INTEGER, required=True, min_value=0
    )
    async def disable(self, ctx: ElevatorInteractionContext, poll_id: int):
        poll = await Poll.from_poll_id(poll_id=poll_id, ctx=ctx)

        if poll:
            await poll.disable(ctx=ctx)


def setup(client):
    PollDisable(client)
