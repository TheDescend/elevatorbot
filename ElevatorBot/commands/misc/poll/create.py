from dis_snek.models import InteractionContext, OptionTypes, slash_option, sub_command

from ElevatorBot.backendNetworking.misc.polls import BackendPolls
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.poll import Poll


class PollCreate(BaseScale):
    @sub_command(
        base_name="poll",
        base_description="Making polls easy",
        sub_name="create",
        sub_description="Create a poll",
    )
    @slash_option(
        name="name",
        description="The name the poll should have",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    @slash_option(
        name="description",
        description="The description the poll should have",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def _poll_create(self, ctx: InteractionContext, name: str, description: str):
        # todo allow images here

        poll = Poll(
            backend=BackendPolls(discord_member=ctx.author, guild=ctx.guild),
            name=name,
            description=description,
            guild=ctx.guild,
            channel=ctx.channel,
            author=ctx.author,
        )
        await poll.send()


def setup(client):
    PollCreate(client)
