from dis_snek.models import InteractionContext, OptionTypes, slash_command, slash_option

from ElevatorBot.backendNetworking.misc.polls import BackendPolls
from ElevatorBot.commandHelpers.subCommandTemplates import poll_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.poll import Poll


class PollDelete(BaseScale):
    @slash_command(
        **poll_sub_command,
        sub_cmd_name="delete",
        sub_cmd_description="Delete a poll",
    )
    @slash_option(
        name="poll_id", description="The ID of the poll", opt_type=OptionTypes.INTEGER, required=True, min_value=0
    )
    async def _poll_delete(self, ctx: InteractionContext, poll_id: int):
        backend = BackendPolls(ctx=ctx, discord_member=ctx.author, guild=ctx.guild)

        result = await backend.delete(poll_id=poll_id)
        if not result:
            return

        # also delete the message
        poll = await Poll.from_pydantic_model(client=ctx.bot, data=result)
        await poll.message.delete()


def setup(client):
    PollDelete(client)
