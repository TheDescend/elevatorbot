from dis_snek.models import CommandTypes
from dis_snek.models import context_menu
from dis_snek.models import InteractionContext

from ElevatorBot.commands.base import BaseScale


class MessageMenuCommands(BaseScale):
    """
    Example Message Menu Command
    """

    @context_menu(name="example", context_type=CommandTypes.MESSAGE)
    async def command(self, ctx: InteractionContext):
        message = await ctx.channel.get_message(ctx.target_id)

        # just repeat the original message
        await ctx.send(message.content)


def setup(client):
    client.add_cog(MessageMenuCommands(client))
