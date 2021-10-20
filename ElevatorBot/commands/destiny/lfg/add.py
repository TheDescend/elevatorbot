from dis_snek.models import InteractionContext
from dis_snek.models import Member
from dis_snek.models import OptionTypes
from dis_snek.models import slash_option
from dis_snek.models import sub_command

from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.lfgSystem import LfgMessage
from ElevatorBot.misc.formating import embed_message


class LfgAdd(BaseScale):
    """This is so cool, it adds people into the main roster even if full"""

    @sub_command(
        base_name="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        sub_name="add",
        sub_description="Add a user to an lfg event",
    )
    @slash_option(name="lfg_id", description="The lfg message id", required=True, opt_type=OptionTypes.INTEGER)
    @default_user_option(description="The user you want to add", required=True)
    async def _add(self, ctx: InteractionContext, lfg_id: int, user: Member):
        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if type(lfg_message) is BackendResult:
            await lfg_message.send_error_message(ctx=ctx, hidden=True)
            return

        if await lfg_message.add_joined(user, force_into_joined=True):
            embed = embed_message(
                "Success",
                f"{user.display_name} has been added to the LFG post with the id `{lfg_id}`",
            )
        else:
            embed = embed_message(
                "Error",
                f"{user.display_name} could not be added to the LFG post with the id `{lfg_id}`, because they are already in it or they are blacklisted by the creator",
            )

        await ctx.send(ephemeral=True, embeds=embed)


def setup(client):
    LfgAdd(client)
