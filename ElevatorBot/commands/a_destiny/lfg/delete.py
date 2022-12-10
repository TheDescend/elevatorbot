from naff import slash_command

from ElevatorBot.commandHelpers.optionTemplates import lfg_event_id
from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.destiny.lfg.lfgSystem import LfgMessage
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.discordShortcutFunctions import has_admin_permission
from ElevatorBot.misc.formatting import embed_message


class LfgDelete(BaseModule):
    @slash_command(
        **lfg_sub_command,
        sub_cmd_name="delete",
        sub_cmd_description="When you fucked up and need to delete an event",
        dm_permission=False,
    )
    @lfg_event_id()
    async def delete(self, ctx: ElevatorInteractionContext, lfg_id: int):
        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(ctx=ctx, lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if not lfg_message:
            return

        # test if the user is admin or author
        if ctx.author.id != lfg_message.author_id:
            if not await has_admin_permission(ctx=ctx, member=ctx.author):
                return

        await lfg_message.delete(hard=True)
        await ctx.send(
            ephemeral=True,
            embeds=embed_message("Success", f"The LFG event with the id `{lfg_id}` has been deleted"),
        )


def setup(client):
    LfgDelete(client)
