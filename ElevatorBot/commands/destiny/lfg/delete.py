from dis_snek.models import InteractionContext, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.lfg.lfgSystem import LfgMessage
from ElevatorBot.misc.discordShortcutFunctions import has_admin_permission
from ElevatorBot.misc.formating import embed_message


class LfgDelete(BaseScale):
    @slash_command(
        **lfg_sub_command,
        sub_cmd_name="delete",
        sub_cmd_description="When you fucked up and need to delete an event",
    )
    @slash_option(
        name="lfg_id", description="The lfg message id", required=True, opt_type=OptionTypes.INTEGER, min_value=0
    )
    async def _delete(self, ctx: InteractionContext, lfg_id: int):
        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(ctx=ctx, lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if not lfg_message:
            return

        # test if the user is admin or author
        if ctx.author.id != lfg_message.author.id:
            if not await has_admin_permission(ctx=ctx, member=ctx.author):
                return

        await lfg_message.delete()
        await ctx.send(
            ephemeral=True,
            embeds=embed_message("Success", f"The LFG post with the id `{lfg_id}` has been deleted"),
        )


def setup(client):
    LfgDelete(client)
