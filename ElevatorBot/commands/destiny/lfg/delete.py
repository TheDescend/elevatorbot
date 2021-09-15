from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.core.destiny.lfgSystem import LfgMessage
from ElevatorBot.misc.formating import embed_message


class LfgDelete(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="delete",
        description="When you fucked up and need to delete an event",
        options=[
            create_option(
                name="lfg_id",
                description="The lfg message id",
                option_type=4,
                required=True,
            ),
        ],
    )
    async def _delete(self, ctx: SlashContext, lfg_id: int):
        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if type(lfg_message) is BackendResult:
            await lfg_message.send_error_message(ctx=ctx, hidden=True)
            return

        await lfg_message.delete()
        await ctx.send(
            hidden=True,
            embed=embed_message("Success", f"The LFG post with the id `{lfg_id}` has been deleted"),
        )


def setup(client):
    client.add_cog(LfgDelete(client))
