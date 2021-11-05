from dis_snek.models import (
    InteractionContext,
    Member,
    OptionTypes,
    slash_command,
    slash_option,
)

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.lfgSystem import LfgMessage
from ElevatorBot.misc.formating import embed_message


class LfgKick(BaseScale):
    @slash_command(
        **lfg_sub_command,
        sub_cmd_name="kick",
        sub_cmd_description="Kick a user from an lfg event",
    )
    @slash_option(
        name="lfg_id", description="The lfg message id", required=True, opt_type=OptionTypes.INTEGER, min_value=0
    )
    @default_user_option(description="The user you want to kick", required=True)
    async def _kick(self, ctx: InteractionContext, lfg_id: int, user: Member):
        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(ctx=ctx, lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if not lfg_message:
            return

        if await lfg_message.remove_member(user):
            embed = embed_message(
                "Success",
                f"{user.display_name} has been removed from the LFG post with the id `{lfg_id}`",
            )

        else:
            embed = embed_message(
                "Error",
                f"{user.display_name} could not be deleted from the LFG post with the id `{lfg_id}`, because they are not in it",
            )

        await ctx.send(ephemeral=True, embeds=embed)


def setup(client):
    LfgKick(client)
