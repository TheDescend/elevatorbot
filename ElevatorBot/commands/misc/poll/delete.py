from dis_snek.models import InteractionContext, OptionTypes, slash_option, sub_command

from ElevatorBot.backendNetworking.misc.polls import BackendPolls
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.poll import Poll


class PollDelete(BaseScale):
    @sub_command(
        base_name="poll",
        base_description="Making polls easy",
        sub_name="delete",
        sub_description="Delete a poll",
    )
    @slash_option(
        name="poll_id",
        description="The ID of the poll",
        opt_type=OptionTypes.INTEGER,
        required=True,
    )
    async def _poll_delete(self, ctx: InteractionContext, poll_id: int):
        backend = BackendPolls(discord_member=ctx.author, guild=ctx.guild)

        result = await backend.delete(poll_id=poll_id)
        if not result:
            await result.send_error_message(ctx=ctx, hidden=False)
            return

        # also delete the message
        poll = await Poll.from_dict(client=ctx.bot, data=result.result)
        await poll.message.delete()


def setup(client):
    PollDelete(client)
