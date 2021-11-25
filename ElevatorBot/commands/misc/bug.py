from dis_snek.models import InteractionContext, OptionTypes, slash_command, slash_option

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.descendOnlyIds import descend_channels


class Bug(BaseScale):
    @slash_command(name="bug", description="Use this if you want to report any bugs to the developer")
    @slash_option(
        name="message",
        description="Please describe the bug you have noticed",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def _bug(self, ctx: InteractionContext, message: str):
        embed = embed_message("Bug Report", f"{message}\n⁣\n- by {ctx.author.mention}")
        await descend_channels.bot_dev_channel.send(embeds=embed)

        await ctx.send(
            ephemeral=True,
            embeds=embed_message(
                "Success",
                "Your message has been forwarded to my developer\nDepending on the clarity of your bug report, you may or may not be contacted by them",
            ),
        )


def setup(client):
    Bug(client)
