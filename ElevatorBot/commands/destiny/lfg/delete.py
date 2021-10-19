from dis_snek.models import InteractionContext
from dis_snek.models import OptionTypes
from dis_snek.models import slash_option
from dis_snek.models import sub_command

from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.commandHelpers.optionTemplates import destiny_group
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.lfgSystem import LfgMessage
from ElevatorBot.misc.formating import embed_message


class LfgDelete(BaseScale):
    @sub_command(
        base_name="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        sub_name="delete",
        sub_description="When you fucked up and need to delete an event",
        **destiny_group,
    )
    @slash_option(name="lfg_id", description="The lfg message id", required=True, opt_type=OptionTypes.INTEGER)
    async def _delete(self, ctx: InteractionContext, lfg_id: int):
        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if type(lfg_message) is BackendResult:
            await lfg_message.send_error_message(ctx=ctx, hidden=True)
            return

        await lfg_message.delete()
        await ctx.send(
            ephemeral=True,
            embeds=embed_message("Success", f"The LFG post with the id `{lfg_id}` has been deleted"),
        )


def setup(client):
    LfgDelete(client)
