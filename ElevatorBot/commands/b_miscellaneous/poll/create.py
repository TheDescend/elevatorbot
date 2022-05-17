from naff import Attachment, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.subCommandTemplates import poll_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.poll import Poll
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.networking.misc.polls import BackendPolls


class PollCreate(BaseModule):
    @slash_command(
        **poll_sub_command,
        sub_cmd_name="create",
        sub_cmd_description="Create a new poll",
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
    @slash_option(
        name="image",
        description="An image of the problem (press `win` + `shift` + `s`)",
        opt_type=OptionTypes.ATTACHMENT,
        required=False,
    )
    async def create(self, ctx: ElevatorInteractionContext, name: str, description: str, image: Attachment = None):
        poll = Poll(
            backend=BackendPolls(ctx=ctx, discord_member=ctx.author, guild=ctx.guild),
            name=name,
            description=description,
            image_url=image.url if image else None,
            guild=ctx.guild,
            channel=ctx.channel,
            author=ctx.author,
        )
        await poll.send(ctx=ctx)


def setup(client):
    PollCreate(client)
